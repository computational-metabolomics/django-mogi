def summarise_inputdata_annotations(conn, rank_limit=50):
    # Creat two summary tables (one for LC and one for DIMS and then output
    # to single csv file
    c = conn.cursor()
    sql_stmt = """
       SELECT
       'dims' AS ms_type, 
       sp.sid,
       '' AS grpid,
       '' AS grp_name,
       round(sp.mz, 8) AS mz,
       round(sp.i, 2) AS i,
       round(spm.well_rt, 3) AS rt,
       round(spm.well_rtmin,3) AS rtmin,
       round(spm.well_rtmax,3) AS rtmax,
       sp.adduct AS camera_adduct,
       sp.isotopes AS camera_isotopes,
       GROUP_CONCAT(DISTINCT (CAST (cpgXsp.grpid AS INTEGER) ) ) AS lc_grpid_mtchs,
       '' AS dims_sid_mtchs,
       spm.well,  
       mc.inchi,
       mc.inchikey,
       mc.inchikey1,
       mc.inchikey2,
       mc.inchikey3,
       mc.name,
       mc.exact_mass,
       mc.molecular_formula,
       mc.pubchem_cids,
       mc.kegg_cids,
       mc.kegg_brite,
       mc.kegg_drugs,
       mc.hmdb_ids,
       mc.hmdb_bio_custom_flag,
       mc.hmdb_drug_flag,
       mc.biosim_max_count,
       mc.biosim_hmdb_ids,
       '' AS fragmentation_acquistion_num,
       round(sp.dims_predicted_precursor_ion_purity, 3) AS precursor_ion_purity,
       l.accession,
       l.id AS lpid,
       ca.sirius_score,
       ca.sirius_wscore,
       ca.metfrag_score,
       ca.metfrag_wscore,
       ca.sm_score,
       ca.sm_wscore,
       ca.probmetab_score,
       ca.probmetab_wscore,
       ca.ms1_lookup_score,
       ca.ms1_lookup_wscore,
       mc.biosim_max_score,
       ca.biosim_wscore,
       ca.wscore,
       ca.rank,
       ca.adduct_overall
    FROM s_peaks AS sp
       LEFT JOIN
       combined_annotations AS ca ON sp.sid = ca.sid
       LEFT JOIN
       metab_compound AS mc ON ca.inchikey = mc.inchikey
       LEFT JOIN
       l_s_peak_meta AS l ON l.id = ca.sm_lpid
       LEFT JOIN
       s_peak_meta AS spm ON spm.pid = sp.pid
       LEFT JOIN
       c_peak_groups_X_s_peaks AS cpgXsp ON cpgXsp.sid = sp.sid

    WHERE (sp.sid IS NOT NULL) AND (IFNULL(ca.rank<={}, 1)) AND  (
    spm.spectrum_type IS 'dimspy0')
    GROUP BY sp.sid,
             IFNULL(ca.inchikey, sp.sid)
    ORDER BY sp.sid,
             IFNULL(ca.rank, sp.sid)
    """.format(rank_limit)

    r = c.execute(sql_stmt)
    dims_annotations = r.fetchall()

    sql_stmt = """    SELECT 
       'lcms' AS ms_type,
       '' AS sid,
       cpg.grpid,
       cpg.grp_name,
       round(cpg.mz, 8) AS mz,
       ROUND(AVG(cp._into),3) AS i,
       round(cpg.rt, 3) AS rt,
       round(cpg.rtmin,3) AS rtmin,
       round(cpg.rtmax,3) AS rtmax,
       cpg.adduct AS camera_adduct,
       cpg.isotopes AS camera_isotopes,

       '' AS lcms_grpid_mtchs,
       GROUP_CONCAT(DISTINCT (CAST (cpgXsp.sid AS INTEGER) ) ) AS dims_sid_mtchs,
       spm.well,  
       mc.inchi,
       mc.inchikey,
       mc.inchikey1,
       mc.inchikey2,
       mc.inchikey3,
       mc.name,
       mc.exact_mass,
       mc.molecular_formula,
       mc.pubchem_cids,
       mc.kegg_cids,
       mc.kegg_brite,
       mc.kegg_drugs,
       mc.hmdb_ids,
       mc.hmdb_bio_custom_flag,
       mc.hmdb_drug_flag,
       mc.biosim_max_count,
       mc.biosim_hmdb_ids,
       GROUP_CONCAT(DISTINCT(cast(spm.acquisitionNum  as INTEGER) )) AS fragmentation_acquistion_num,
       ROUND(AVG(spm.inPurity),3) AS precursor_ion_purity,
       l.accession,
       l.id AS lpid,
       ca.sirius_score,
       ca.sirius_wscore,
       ca.metfrag_score,
       ca.metfrag_wscore,
       ca.sm_score,
       ca.sm_wscore,
       ca.probmetab_score,
       ca.probmetab_wscore,
       ca.ms1_lookup_score,
       ca.ms1_lookup_wscore,
       mc.biosim_max_score,
       ca.biosim_wscore,
       ca.wscore,
       ca.rank,
       ca.adduct_overall
    FROM c_peak_groups AS cpg
    LEFT JOIN
    combined_annotations AS ca ON ca.grpid=cpg.grpid
    LEFT JOIN
    metab_compound AS mc ON ca.inchikey = mc.inchikey
    LEFT JOIN
    l_s_peak_meta AS l ON l.id = ca.sm_lpid
    LEFT JOIN
    c_peak_groups_X_s_peaks AS cpgXsp ON cpgXsp.grpid = cpg.grpid
    LEFT JOIN
    c_peak_X_c_peak_group AS cpXcpg ON cpXcpg.grpid = cpg.grpid
    LEFT JOIN
    c_peaks AS cp ON cp.cid = cpXcpg.cid
    LEFT JOIN
    c_peak_X_s_peak_meta AS cpXspm ON cpXspm.cid = cp.cid
    LEFT JOIN
    s_peak_meta AS spm ON spm.pid = cpXspm.pid
    LEFT JOIN
    fileinfo AS fi ON fi.fileid = spm.fileid

    WHERE IFNULL(ca.rank<={}, 1) AND fi.class NOT LIKE '%blank%'
    GROUP BY
     cpg.grpid,
     IFNULL(ca.inchikey, cpg.grpid)
    ORDER BY 
     cpg.grpid, 
     IFNULL(ca.rank, cpg.grpid)
    """.format(rank_limit)

    return c.execute(sql_stmt)

