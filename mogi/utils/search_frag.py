from __future__ import print_function
import csv
import os
import tempfile
import sqlite3

from django.core.files import File
import numpy as np
from django.db.models import F, Q
from mogi.models.models_search import (
    SearchFragParam,
    SearchFragResult,
    SearchFragSpectra,
)
from mogi.models.models_datasets import (
    Dataset,
)
from mogi.models.models_isa import (
    Assay,
    AssayDetail
)


def search_frag(sp_id, celery_obj=None):
    if celery_obj:
        celery_obj.update_state(state='RUNNING',
                                meta={'current': 0, 'total': 100, 'status': 'Spectral matching --'})

    sfp = SearchFragParam.objects.get(id=sp_id)

    q_prec_mz = sfp.mz_precursor
    ppm_precursor_tolerance = sfp.ppm_precursor_tolerance
    ra_threshold = sfp.ra_threshold
    ra_diff_threshold = sfp.ra_diff_threshold
    ppm_product_tolerance = sfp.ppm_product_tolerance
    dot_product_score_threshold = sfp.dot_product_score_threshold
    polarities = [i['id'] for i in list(sfp.polarity.all().values('id'))]

    fragspectratypes = [i['short_name'] for i in list(sfp.fragspectratype.all().values('short_name'))]

    metabolite_reference_standard_filter = sfp.metabolite_reference_standard

    products = ['mz,i']
    products.extend(sfp.products.splitlines())

    reader_list = csv.DictReader(products)
    q_mz = np.zeros(len(products) - 1, dtype='float64')
    q_i = np.zeros(len(products) - 1, dtype='float64')
    for i, row in enumerate(reader_list):
        q_mz[i] = row['mz'].strip()
        q_i[i] = row['i'].strip()

    q_ra = q_i / q_i.max() * 100
    q_ra_bool = q_ra > ra_threshold
    q_ra = q_ra[q_ra_bool]
    q_mz = q_mz[q_ra_bool]

    query_prec_low = q_prec_mz - ((q_prec_mz * 0.000001) * ppm_precursor_tolerance)
    query_prec_high = q_prec_mz + ((q_prec_mz * 0.000001) * ppm_precursor_tolerance)

    # Save the query spectra
    sfs = [SearchFragSpectra(searchparam=sfp, mz=mz, ra=ra, query_library='query') for mz, ra in zip(q_mz, q_ra)]

    SearchFragSpectra.objects.bulk_create(sfs)

    datasets = Dataset.objects.filter(polarity_id__in=polarities)

    # Only keep "animal" DMA datasets not those on metabolite reference standards
    if not metabolite_reference_standard_filter:
        datasets = Dataset.objects.filter(metabolite_standard=False)

    dataset_length = len(datasets)
    # loop through the sqlite pths
    cnt = 0
    for dataset in datasets:
        cnt += 1
        if celery_obj:
            celery_obj.update_state(state='RUNNING',
                                    meta={'current': round(cnt/dataset_length*100.0, 2), 'total': 100,
                                          'status': 'Spectral matching -- {} of {} datasets -- currently on file {}'.format(
                                              cnt, dataset_length,
                                              os.path.basename(dataset.sqlite.path))
                                          })

        # read in sqlite
        conn = sqlite3.connect(dataset.sqlite.path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        spectra_type_string = "('" + "', '".join(fragspectratypes) + "')"

        sql_stmt = """
              SELECT
              pid,
              grpid,
              spectrum_type,
              precursor_mz,
              spm.name AS spectrum_details,
              (precursor_mz + ((precursor_mz * 0.000001) * {ppm})) AS library_prec_high,
              (precursor_mz - ((precursor_mz * 0.000001) * {ppm})) AS library_prec_low
           FROM s_peak_meta AS spm 
           WHERE spm.spectrum_type IN {st} AND
           {query_prec_high} >= library_prec_low AND library_prec_high>={query_prec_low}
           """.format(ppm=ppm_precursor_tolerance, query_prec_low=query_prec_low, query_prec_high=query_prec_high,
                      st=spectra_type_string)
        r = c.execute(sql_stmt)

        precursors = [row for row in r]
        print(precursors)
        for precursor in precursors:

            pid = precursor['pid']
            grpid = precursor['grpid']
            spectrum_type = precursor['spectrum_type']
            l_prec_mz = precursor['precursor_mz']
            spectrum_details = precursor['spectrum_details']

            ppmdiff = 1e6 * (q_prec_mz - l_prec_mz) / l_prec_mz

            r = c.execute("SELECT mz, i, ra FROM s_peaks AS sp WHERE sp.pid=={}".format(pid))
            l_mz = []
            l_i = []

            for row in r:
                l_mz.append(row['mz'])
                l_i.append(row['i'])

            l_mz = np.array(l_mz)
            l_i = np.array(l_i)

            l_ra = l_i / l_i.max() * 100
            ra_bool = l_ra > ra_threshold
            l_ra = l_ra[ra_bool]
            l_mz = l_mz[ra_bool]

            # Extract out the library mz and library intensity
            # Perform the spectral match
            dpc = spectral_match(q_mz, l_mz, q_ra, l_ra, ppm_product_tolerance, ra_diff_threshold, weight_mz=2,
                                 weight_ra=0.5)

            if dpc >= dot_product_score_threshold:
                print('match!')
                ############################
                # LC-MS averaged match
                ############################
                # Get 'lcms' match information (for averaged spectra)
                if spectrum_type in ['inter', 'intra']:
                    print('LC-MS average')
                    sql_stmt = """ 
                               SELECT 
                                  ca.grpid, cpg.rt, '' AS sid, ca.inchikey, mc.inchikey1, mc.name, 
                                  ROUND(ca.wscore,2) AS wscore, '' AS well
                               FROM combined_annotations AS ca 
                               LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                               LEFT JOIN c_peak_groups as cpg ON cpg.grpid=ca.grpid
                               WHERE ca.grpid=={} AND ca.rank==1 
                               LIMIT 1
                               """.format(grpid)

                ############################
                # LC-MS scan match
                ############################
                # Get 'lcms' match information (for individual scan spectra)
                elif spectrum_type == 'scan':
                    print('LC-MS scan')
                    sql_stmt = """
                                  SELECT 
                                     ca.grpid, cpg.rt, '' AS sid, ca.inchikey, mc.inchikey1, mc.name, 
                                     ROUND(ca.wscore,2) AS wscore, '' AS well
                               FROM combined_annotations AS ca 
                               LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                               LEFT JOIN c_peak_groups as cpg ON cpg.grpid=ca.grpid
                               LEFT JOIN c_peak_X_c_peak_group AS cpXcpg ON cpXcpg.grpid = cpg.grpid
                               LEFT JOIN c_peaks AS cp ON cp.cid = cpXcpg.cid
                               LEFT JOIN c_peak_X_s_peak_meta AS cpXspm ON cp.cid = cpXspm.cid
                               LEFT JOIN s_peak_meta AS spm ON spm.pid = cpXspm.pid
                               WHERE spm.pid=={} AND ca.rank==1
                               GROUP BY ca.inchikey
                               LIMIT 1
                                """.format(pid)
                ############################
                # DIMS match
                ############################
                # Get DIMSn match details
                elif spectrum_type == 'msnpy':
                    print('msnpy')
                    sql_stmt = """SELECT '' AS grpid, ca.sid, ca.inchikey,  mc.name, ROUND(ca.wscore,2) AS wscore,
                                  spm.well, spm.well_rt AS rt
                            FROM s_peak_meta AS spm1 
                            LEFT JOIN s_peak_meta_X_s_peaks AS sxs ON spm1.pid=sxs.pid
                            LEFT JOIN
                                s_peaks_X_s_peaks AS spXsp ON spXsp.sid2 = sxs.sid
                            LEFT JOIN s_peaks AS sp ON sp.sid=spXsp.sid1
                            LEFT JOIN s_peak_meta AS spm ON spm.pid=sp.pid
                            LEFT JOIN combined_annotations AS ca ON spXsp.sid1=ca.sid
                            LEFT JOIN metab_compound as mc ON mc.inchikey=ca.inchikey 
                            WHERE spm1.pid=={} AND ca.rank==1
                            LIMIT 1
                           """.format(pid)
                else:
                    sql_stmt = ""
                    continue

                combined = c.execute(sql_stmt)

                summary_details = [row for row in combined]

                # Check if there are any annotations (won't always be the case - due to the combining process and cutoffs)
                if len(summary_details) == 0:
                    sid = None
                    top_annotation = None
                    top_wscore = None
                    well = None
                    rt = None
                else:
                    summary_details = summary_details[0]
                    sid = summary_details['sid']

                    top_annotation = '{} {}'.format(summary_details['inchikey'], summary_details['name'])
                    top_wscore = summary_details['wscore']

                    well = summary_details['well']
                    rt = summary_details['rt']

                # Get best spectral match annotation
                sql_stmt = """SELECT inchikey, library_compound_name, library_source_name, ROUND(dpc, 2) AS dpc
                                FROM sm_matches AS sm
                                    WHERE qpid={}
                                    ORDER BY -dpc
                                    LIMIT 1
                                           """.format(pid)
                sm = c.execute(sql_stmt)
                summary_spectral_match = [row for row in sm]

                if len(summary_spectral_match) == 0:
                    top_spectral_match = None
                else:
                    summary_spectral_match = summary_spectral_match[0]
                    top_spectral_match = '{} {} {} {}'.format(summary_spectral_match['inchikey'],
                                                              summary_spectral_match['library_compound_name'],
                                                              summary_spectral_match['library_source_name'],
                                                              summary_spectral_match['dpc']
                                                              )

                # Get best metfrag annotation
                if spectrum_type in ['msnpy']:
                    sql_stmt = """SELECT InChIkey, CompoundName, ROUND(Score, 2) AS score
                               FROM metfrag_results WHERE pid=={}
                               LIMIT 1
                                           """.format(pid)
                elif spectrum_type in ['inter', 'intra']:
                    sql_stmt = """SELECT InChIkey, CompoundName, ROUND(Score, 2) AS score
                                                   FROM metfrag_results WHERE grpid=={}
                                                   LIMIT 1
                                                               """.format(pid)
                else:
                    sql_stmt = ""

                mf = c.execute(sql_stmt)
                summary_metfrag_match = [row for row in mf]

                if len(summary_metfrag_match) == 0:
                    top_metfrag = None
                else:
                    summary_metfrag_match = summary_metfrag_match[0]
                    top_metfrag = '{} {} {}'.format(summary_metfrag_match['inchikey'],
                                                    summary_metfrag_match['CompoundName'],
                                                    summary_metfrag_match['score'])

                # Get best sirius annotation
                if spectrum_type in ['msnpy']:
                    # Don't have the anem recorded for DIMSn analysis
                    sql_stmt = """SELECT InChikey2D, '' AS name, rank
                               FROM sirius_csifingerid_results
                                WHERE pid=={}
                                LIMIT 1
                                           """.format(pid)
                elif spectrum_type in ['inter', 'intra']:
                    sql_stmt = """ SELECT InChikey2D, name, rank
                                    FROM sirius_csifingerid_results
                                    WHERE grpid=={}
                                LIMIT 1
                               """.format(grpid)
                else:
                    sql_stmt = ""

                sirius = c.execute(sql_stmt)
                summary_sirius_match = [row for row in sirius]

                if len(summary_sirius_match) == 0:
                    top_sirius_csi_fingerid = None
                else:
                    summary_sirius_match = summary_sirius_match[0]
                    top_sirius_csi_fingerid = '{} {} {}'.format(summary_sirius_match['InChikey2D'],
                                                                summary_sirius_match['name'],
                                                                summary_sirius_match['rank'])


                sfr = SearchFragResult(searchparam=sfp,
                                       dpc=np.round(dpc, 4),
                                       ppm_diff_prec=np.round(ppmdiff,2),
                                       l_prec_mz=np.round(l_prec_mz, 6),
                                       q_prec_mz=np.round(q_prec_mz, 6),
                                       rt=np.round(rt, 3) if rt else None,
                                       well=well,
                                       dataset_pid=pid,
                                       dataset_grpid=grpid if grpid else None,
                                       dataset_sid=sid if sid else None,
                                       top_combined_annotation=top_annotation,
                                       top_spectral_match=top_spectral_match,
                                       top_sirius_csifingerid=top_sirius_csi_fingerid,
                                       top_metfrag=top_metfrag,
                                       top_wscore=top_wscore,
                                       spectrum_type=spectrum_type,
                                       spectrum_details=spectrum_details,
                                       dataset=dataset)
                sfr.save()


def spectral_match(q_mz, l_mz, q_ra, l_ra, ppm_threshold, ra_diff_threshold, weight_mz=2, weight_ra=0.5):
    # weight the peaks
    q_w = np.power(q_ra, weight_ra) * np.power(q_mz, weight_mz)
    l_w = np.power(l_ra, weight_ra) * np.power(l_mz, weight_mz)

    # align peaks
    aligned_peaks = align_peaks(q_mz, l_mz, q_ra, l_ra, q_w, l_w, ppm_threshold, ra_diff_threshold)

    # perform similarity measure
    sm_out = cossim(aligned_peaks[0], aligned_peaks[1])

    return sm_out


def compare_nan_array(func, a, thresh):
    # https://stackoverflow.com/questions/47340000/how-to-get-rid-of-runtimewarning-invalid-value-encountered-in-greater
    # prevents na warnings (not necessary but just stops people worrying when they see the warnings!)
    out = ~np.isnan(a)
    out[out] = func(a[out], thresh)
    return out


class AlignTable(object):
    def __init__(self, init_l):
        self.d_table = np.array(init_l, dtype=[('peakID', 'int64'),
                                               ('mz', 'float64'),
                                               ('ra', 'float64'),
                                               ('w', 'float64'),
                                               ('query', 'bool_')  # True for query False for library
                                               ])
        self.current_peak = 0
        self.query_values = ''
        #
        self.library_values = ''

    def add_peak(self, peakID, mz, ra, w, query_bool):
        self.d_table['peakID'][self.current_peak] = peakID
        self.d_table['mz'][self.current_peak] = mz
        self.d_table['ra'][self.current_peak] = ra
        self.d_table['w'][self.current_peak] = w
        self.d_table['query'][self.current_peak] = query_bool
        self.current_peak += 1

    def get_aligned_arrays(self, type_='w'):
        self.query_values = self.d_table[(self.d_table['query'] == True) & (self.d_table['peakID'] >= 0)][type_]
        self.library_values = self.d_table[(self.d_table['query'] == False) & (self.d_table['peakID'] >= 0)][type_]
        return np.array([self.query_values, self.library_values])


def align_peaks(q_mz, l_mz, q_ra, l_ra, q_w, l_w, ppm_threshold=5, ra_diff_threshold=10):
    # This approach does not check every possible combination but priortises the most intense peaks to be matched
    # within the query spectra
    ################################################
    # order the query peaks by relative abundance
    ################################################
    ra_idx = np.argsort(-q_ra)
    q_ra = q_ra[ra_idx]
    q_mz = q_mz[ra_idx]
    q_w = q_w[ra_idx]

    #################################################
    # get distance matrices for both ppm and relative abundance
    #################################################
    ppmdiff = np.zeros((q_mz.shape[0], l_mz.shape[0]), dtype=np.float64)
    radiff = np.zeros((q_mz.shape[0], l_mz.shape[0]), dtype=np.float64)

    for x in range(q_mz.shape[0]):
        for y in range(l_mz.shape[0]):
            # Get ranges of the "sample"
            radiff[x][y] = abs(float(q_ra[x]) - float(l_ra[y]))
            ppmdiff[x][y] = ppm_error(q_mz[x], l_mz[y])

    ###################################################
    # Create peak tracking array
    ###################################################
    # using a numpy structured array (could use a dictionary (which can be faster) but for consistency sticking with
    # numpy https://stackoverflow.com/questions/34933105/speed-up-structured-numpy-array

    # Not the length at the moment is only that of the query. Will be extended at a later as we don't
    # know the full length of the array yet
    # origin is if the peak is for the query or library

    # init_l = zip(tuple(range(0, q_mz.shape[0])), tuple(q_mz), tuple(q_ra), (True,)*q_mz.shape[0])

    init_l = [(-1, 0, 0, 0, 0)] * (
                (q_mz.shape[0] + l_mz.shape[0]) * 2)  # biggest array it could be (e.g. no matches at all)
    at = AlignTable(init_l=init_l)

    lp_remain = np.zeros(l_mz.shape[0])

    ###################################################
    # Get matches for the query
    ###################################################
    # first go through the query finding best match
    mcount = []
    peak_c = 0

    for i in range(0, q_mz.shape[0]):
        peakID = i
        # Add the first peak information from the query
        at.add_peak(i, q_mz[i], q_ra[i], q_w[i], True)

        # get the associated ppm diff and radiff for this query value compared to the library values
        ra_i = radiff[i,]
        ppm_i = ppmdiff[i,]

        if (sum(np.isnan(ra_i)) == ra_i.shape[0]) or (np.nanmin(ppm_i) > ppm_threshold):
            # Check if any of these ppm difference are above are threshold or if all nan. If so no library peaks
            # can be assigned so:
            # Update the library with a miss for this peak id
            at.add_peak(i, 0, 0, 0, False)
            peak_c += 1
            mcount.append('miss')
            continue

        # First check to see if there is a matching mz and intensity value within thresholds
        intenc = ra_i[(compare_nan_array(np.less, ppm_i, ppm_threshold)) &
                      (compare_nan_array(np.less, ra_i, ra_diff_threshold))]

        # Ideally we want a match that has similar ra_diff, but if nothing available will just get the best ppm value
        if intenc.size:
            # get the best intensity for this region
            bool_ = ra_i == np.nanmin(intenc)
        else:
            # just get the smallest ppm error for this region
            bool_ = ppm_i == np.nanmin(ppm_i)

        # update the table with the match
        at.add_peak(i, l_mz[bool_], l_ra[bool_], l_w[bool_], False)
        mcount.append('hit')

        # We remove the difference matrices values for this value as we will not use from now on.
        # This is the weakness with this approach it prioritises the most intense peak in the query
        # and if this peak gets a match first it might miss out on a better match later

        lp_remain[bool_] = None
        ppmdiff[:, bool_] = None
        radiff[:, bool_] = None

    ###################################################
    # Get remaining library values
    ###################################################
    for j in range(0, lp_remain.shape[0]):
        if np.isnan(lp_remain[j]):
            # already been assigned
            continue
        else:
            # Add peak that was not matched previously
            at.add_peak(peakID + j, l_mz[j], l_ra[j], l_w[j], False)

            # add missing values for the query spectra
            at.add_peak(peakID + j, 0, 0, 0, True)

    ###################################################
    # Get the weighted aligned arrays
    ###################################################
    return at.get_aligned_arrays('w')


def ppm_error(obs, theo):
    return abs(1e6 * (obs - theo) / float(theo))


def cossim(A, B):
    return (np.sum(A * B) / np.sqrt(np.sum(np.power(A, 2)) * np.sum(np.power(B, 2))))

# def align_peaks_hungarian(q_mz, l_mz, threshold):
#     # This align peaks approach is based on the 'hungarian method'
#     cost = np.zeros((q_mz.shape[0], l_mz.shape[0]), dtype=np.int64)
#
#     for x in range(q_mz.shape[0]):
#         for y in range(l_mz.shape[0]):
#             cost[x][y] = abs(float(q_mz[x]) - float(l_mz[y]))
#
#     row_ind, col_ind = linear_sum_assignment(cost)
#     new_row = []
#     new_col = []
#     # if you want the pair of indices filtered by the threshold
#     for row, col in zip(row_ind, col_ind):
#         if cost[row, col] < threshold:
#             new_row.append(row)
#         else:
#             new_col.append(col)
#
#     q_mz_out = []
#     for x in range(q_mz.shape[0]):
#         if x in new_row:
#             q_mz_out[]
#
#
#
#
#     pairs = [(row, col) for row, col in zip(row_ind, col_ind)  if cost[row, col] < threshold]
