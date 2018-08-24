from mbrowse.utils.save_lcms import LcmsDataTransfer
from mogi.models import CPeakGroupMetaMOGI, CAnnotationMOGI
from misa.models import Assay, AssayRun, AssayDetail

class LcmsDataTransferMOGI(LcmsDataTransfer):
    cpeakgroupmeta_class = CPeakGroupMetaMOGI
    historydatamogi = ''
    assays = []
    def set_cpeakgroupmeta(self, celery_obj):

        cpgm = CPeakGroupMetaMOGI(metabinputdata=self.md, historydatamogi=self.historydatamogi)
        cpgm.save()

        ########################################
        # Check ISA has been created for files
        ########################################
        # if the files are not assigned to an assay we can't process properly as we can not reference to the correct
        # study sample
        for mfile in self.mfile_d.values():
            if not mfile.run.assayrun:
                if celery_obj:
                    celery_obj.update_state(state='FAILED',
                                                meta={'current': 0, 'total': 100,
                                                      'status': 'Data file {} used is not associated with any '
                                                                'Assay '.format(mfile.original_filename)})

                return 0

        ###########################################
        # Get relevant assays
        ###########################################

        assays = [Assay.objects.get(id=mfile.run.assayrun.assaydetail.assay_id) for mfile in set(self.mfile_d.values())]
        assays = list(set(assays))

        md_name = '|'

        for a in assays:
            md_name += '{} {} {}|'.format(a.study.investigation_id, a.study_id, a.name)
            cpgm.assay.add(a)

        self.md.name = md_name
        self.assays = assays
        return cpgm

