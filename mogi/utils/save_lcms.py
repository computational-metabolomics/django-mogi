from metab.utils.save_lcms import LcmsDataTransfer
from mogi.models import CPeakGroupMetaMOGI
from misa.models import Assay

class LcmsDataTransferMOGI(LcmsDataTransfer):
    cpeakgroupmeta_class = CPeakGroupMetaMOGI
    historydatamogi = ''

    def set_cpeakgroupmeta(self):
        print 'CPeakGroupMetaMOGI'
        mfile_values = self.mfiles.values('run__assayrun__assaydetail__assay_id')

        cpgm = CPeakGroupMetaMOGI(metabinputdata=self.md, historydatamogi=self.historydatamogi)
        cpgm.save()
        for m in mfile_values:
            cpgm.assay.add(Assay.objects.get(id=m['run__assayrun__assaydetail__assay_id']))
        return cpgm
