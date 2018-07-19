from mbrowse.utils.save_lcms import LcmsDataTransfer
from mogi.models import CPeakGroupMetaMOGI, CAnnotationMOGI
from misa.models import Assay

class LcmsDataTransferMOGI(LcmsDataTransfer):
    cpeakgroupmeta_class = CPeakGroupMetaMOGI
    historydatamogi = ''
    assays = []
    def set_cpeakgroupmeta(self):

        cpgm = CPeakGroupMetaMOGI(metabinputdata=self.md, historydatamogi=self.historydatamogi)
        cpgm.save()


        assays = [Assay.objects.get(id=mfile.run.assayrun.assaydetail.assay_id) for mfile in set(self.mfile_d.values())]
        assays = list(set(assays))
        for a in assays:
            cpgm.assay.add(a)

        self.assays = assays
        return cpgm

