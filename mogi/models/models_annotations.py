from django.db import models

class CombinedAnnotation(models.Model):
    dataset_id = models.IntegerField(blank=True, null=True)
    inchikey = models.CharField(max_length=254, blank=True, null=True)
    inchikey1 = models.CharField(max_length=254, blank=True, null=True)

    compound_name = models.TextField(blank=True, null=True)
    ms_type = models.CharField(max_length=254, blank=True, null=True)
    sid = models.IntegerField(blank=True, null=True)
    grpid = models.IntegerField(blank=True, null=True)
    grp_name = models.CharField(max_length=254, blank=True, null=True)
    mz = models.FloatField(blank=True, null=True)
    sm_lpid = models.IntegerField(blank=True, null=True)
    pubchem_cids = models.CharField(max_length=254, blank=True, null=True)

    rt = models.FloatField(blank=True, null=True)
    well = models.CharField(max_length=1024, blank=True, null=True)

    sirius_score = models.FloatField(blank=True, null=True)
    sirius_wscore = models.FloatField(blank=True, null=True)
    metfrag_score = models.FloatField(blank=True, null=True)
    metfrag_wscore = models.FloatField(blank=True, null=True)
    sm_score = models.FloatField(blank=True, null=True)
    sm_wscore = models.FloatField(blank=True, null=True)
    ms1_lookup_score = models.FloatField(blank=True, null=True)
    ms1_lookup_wscore = models.FloatField(blank=True, null=True)
    biosim_max_score = models.FloatField(blank=True, null=True)
    biosim_wscore = models.FloatField(blank=True, null=True)
    wscore = models.FloatField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    adduct_overall = models.TextField(blank=True, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)


class SpectralMatching(models.Model):
    dataset_id = models.IntegerField(blank=True, null=True)
    inchikey = models.CharField(max_length=254, blank=True, null=True)
    mid = models.IntegerField(blank=True, null=True)
    lpid = models.IntegerField(blank=True, null=True)
    qpid = models.IntegerField(blank=True, null=True)
    dpc = models.FloatField(blank=True, null=True)
    rdpc = models.FloatField(blank=True, null=True)
    cdpc = models.FloatField(blank=True, null=True)
    mcount = models.IntegerField(blank=True, null=True)
    allcount  = models.IntegerField(blank=True, null=True)
    mpercent = models.FloatField(blank=True, null=True)
    library_rt = models.FloatField(blank=True, null=True)
    query_rt = models.FloatField(blank=True, null=True)
    rtdiff = models.FloatField(blank=True, null=True)
    library_precursor_mz = models.FloatField(blank=True, null=True)
    query_precursor_mz = models.FloatField(blank=True, null=True)
    library_accession = models.TextField(blank=True, null=True)
    library_precursor_type= models.CharField(max_length=254, blank=True, null=True)
    library_entry_name= models.TextField(blank=True, null=True)
    library_source_name= models.CharField(max_length=254, blank=True, null=True)
    library_compound_name= models.TextField(blank=True, null=True)


    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)


class MetFrag(models.Model):
    dataset_id = models.IntegerField(blank=True, null=True)
    inchikey = models.CharField(max_length=254, blank=True, null=True)
    inchikey1 = models.CharField(max_length=254, blank=True, null=True)
    inchikey2 = models.CharField(max_length=254, blank=True, null=True)
    inchikey3 = models.CharField(max_length=254, blank=True, null=True)

    sample_name = models.CharField(max_length=254, blank=True, null=True)
    mz  = models.FloatField(blank=True, null=True)
    grpid = models.IntegerField(blank=True, null=True)
    rt = models.FloatField(blank=True, null=True)
    adduct  = models.CharField(max_length=254, blank=True, null=True)
    compound_name = models.TextField(blank=True, null=True)
    expl_peaks = models.TextField(blank=True, null=True)
    formulas_of_expl_peaks = models.TextField(blank=True, null=True)
    fragmenter_score = models.FloatField(blank=True, null=True)
    fragmenter_score_values= models.TextField(blank=True, null=True)
    identifier = models.TextField(blank=True, null=True)
    inchi  = models.TextField(blank=True, null=True)
    maximum_tree_depth = models.CharField(max_length=254, blank=True, null=True)
    molecular_formula = models.TextField(blank=True, null=True)
    monoisotopic_mass = models.FloatField(blank=True, null=True)
    no_expl_peaks = models.CharField(max_length=254, blank=True, null=True)
    number_peaks_used= models.CharField(max_length=254, blank=True, null=True)
    file= models.TextField(blank=True, null=True)
    offline_met_fusion_score = models.FloatField(blank=True, null=True)
    smiles = models.TextField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    suspect_list_score  = models.FloatField(blank=True, null=True)
    xlogp3 = models.FloatField(blank=True, null=True)
    pid = models.IntegerField(blank=True, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)



class SiriusCSIFingerID(models.Model):
    dataset_id = models.IntegerField(blank=True, null=True)
    mz = models.FloatField(blank=True, null=True)
    rt = models.FloatField(blank=True, null=True)
    grpid = models.IntegerField(blank=True, null=True)
    file = models.TextField(blank=True, null=True)
    adduct = models.CharField(max_length=1024, blank=True, null=True)

    rank = models.IntegerField(blank=True, null=True)
    formula_rank = models.IntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    molecular_formula = models.TextField(blank=True, null=True)

    inchikey2 = models.CharField(max_length=254, blank=True, null=True)
    inchi = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True)
    smiles = models.TextField(blank=True, null=True)
    xlogp = models.FloatField(blank=True, null=True)
    pubchemids = models.CharField(max_length=254, blank=True, null=True)
    links = models.TextField(blank=True, null=True)
    dbflags = models.TextField(blank=True, null=True)
    bounded_score = models.FloatField(blank=True, null=True)

    pid = models.IntegerField(blank=True, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.id)
