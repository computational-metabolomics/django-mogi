from metab.utils.save_lcms import LcmsDataTransfer
from mogi.models import CPeakGroupMetaMOGI, HistoryDataMOGI
from misa.models import Assay

class LcmsDataTransferMOGI(LcmsDataTransfer):
    cpeakgroupmeta_class = CPeakGroupMetaMOGI
    historydatamogi = ''

    def set_cpeakgroupmeta(self):
        CPeakGroupMeta = self.cpeakgroupmeta_class

        # mfile_values = self.mfiles.values('run__assayrun__assaydetail__assay',
        #               'run__assayrun__assaydetail__assay__study',
        #               'run__assayrun__assaydetail__assay__study__investigation')
        mfile_values = self.mfiles.values('run__assayrun__assaydetail__assay_id')


        cpgm = CPeakGroupMeta(metabinputdata=self.md, historydatamogi=self.historydatamogi)
        cpgm.save()
        for m in mfile_values:
            cpgm.assay.add(Assay.objects.get(id=m['run__assayrun__assaydetail__assay_id']))




        return cpgm
