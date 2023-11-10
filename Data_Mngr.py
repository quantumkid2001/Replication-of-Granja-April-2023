#from Setup_Mngr import Setup_Mngr
#from scipy.stats import pearsonr
import pandas as pd
import numpy as np
#import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

class Data_Mngr:
    
    def __init__(self,config_file,s_ddt, e_ddt):
        self.var_config = pd.read_excel(config_file,sheet_name="call_vars")
        self.mnemonics = self.var_config.mnemonic
        self.ddt_start = s_ddt 
        self.ddt_end = e_ddt
        self.cr_schedules = self.var_config["schedule"].unique()
        self.the_idates = []
        self.the_ddates = []
        
    def get_fdic_data(self,idate):
        fn = "C:\\work\\frbsf_code_sample\\fdic_data\\" + idate + ".csv"
        fdic_data = pd.read_csv(fn,keep_default_na=False)
        fdic_data = fdic_data[['Cert/ID', 'Institution Name', 'City', 'State', 'Class']]
        fdic_data = fdic_data.rename(columns={'Cert/ID':'cert','Institution Name':'name','City':'city','State':'state','Class':'class' })
        
        return(fdic_data)
    
    def get_fdic_qbr_info_file(self,idate):
        pth = self.generate_file_path(idate)
        fn =  "FFIEC CDR Call Bulk POR " + idate + ".txt" #03312019#self.generate_file_name("POR",idate)
        qbr_data = pd.read_csv(pth+fn,keep_default_na=False,delimiter="\t")
        return(qbr_data)

    def get_data_file(self,isched,idate,ddate):
        pth = self.generate_file_path(idate)
        fn =  self.generate_file_name(isched,idate)
        temp_data = pd.read_csv(pth + fn, delimiter = '\t',keep_default_na=False,low_memory=False)
        temp_data = temp_data[temp_data["IDRSSD"] != '']
        temp_data.IDRSSD = temp_data.IDRSSD.astype(int)
        
        #get fdic data to get commercial and savings banks in order to match data
        fdic_data = self.get_fdic_data(idate)
        
        #get qbr bank info to merge certs to get idrssd
        qbr_data = self.get_fdic_qbr_info_file(idate)
        qbr_data = qbr_data[["IDRSSD","FDIC Certificate Number"]]
        qbr_data = qbr_data.rename(columns={"IDRSSD":"IDRSSD","FDIC Certificate Number":"cert"})
        
        idrssd_qbr_banks = pd.merge(fdic_data, qbr_data, on='cert', how='outer')
        output = pd.merge(idrssd_qbr_banks, temp_data, on='IDRSSD', how='outer')
        return(output)

    def create_full_data_set(self):
        self.all_data = None
        self.generate_file_idates(self.ddt_start,self.ddt_end)
        self.generate_file_ddates(self.ddt_start,self.ddt_end)
        for i in range(0,len(self.the_idates)):
            df_date = None
            for j in range(0,len(self.cr_schedules)):
                temp_vars = self.var_config[self.var_config["schedule"] == self.cr_schedules[j]]
                temp_vars = temp_vars["mnemonic"]
                temp_vars = np.append("IDRSSD",temp_vars)
                
                temp_data = self.get_data_file(self.cr_schedules[j], self.the_idates[i],self.convert_file_date_to_ddt(self.the_idates[i]))
                temp_data = temp_data[temp_vars]
                
                if df_date is None:
                    df_date = temp_data
                else:
                    df_date = pd.merge(df_date,temp_data,on="IDRSSD")
                    
            df_date["ddt"] = self.convert_file_date_to_ddt(self.the_idates[i])
            if self.all_data is None:
                self.all_data = df_date
            else:
                self.all_data = pd.concat([self.all_data,df_date]) 
            print(self.the_idates[i])

    def format_ddt_for_file(self,ddt):
        yr = ddt[0:4]
        mm = ddt[5:7]
        dd = ddt[8:10]
        ddt = mm+dd+yr
        return(ddt)
    
    def get_ddt_yr(self,the_date):
        return(the_date[0:4])
    
    def get_ddt_mm(self,the_date):
        return(the_date[5:7])
    
    def get_ddt_dd(self,the_date):
        return(the_date[8:10])
    
    def generate_file_path(self,the_date):
        the_path = "C:\\work\\frbsf_code_sample\\data\\FFIEC CDR Call Bulk All Schedules " + the_date + "\\"
        return(the_path)
    
    def generate_file_name(self,schedule,the_idate):
        if (schedule == "RCB" and self.convert_file_date_to_ddt(the_idate) > "2009-03-31") or (schedule == "RCO" and self.convert_file_date_to_ddt(the_idate) > "2013-03-31"):
           the_file = "FFIEC CDR Call Schedule " + schedule + " " +  the_idate + "(1 of 2).txt"
        else:
            the_file = "FFIEC CDR Call Schedule " + schedule + " " +  the_idate + ".txt"
        return(the_file)
    
    def generate_file_idates(self,ddt_start,ddt_end):
        yvec = range(int(self.get_ddt_yr(ddt_start)),int(self.get_ddt_yr(ddt_end)))
        dvec = ["31","30","30","31"]
        mvec = ["03","06","09","12"]
        qvec = ["0331","0630","0930","1231"]
        yvec = range(int(self.ddt_start[0:4]),int(self.ddt_end[0:4])+1)
        the_dates = []
        for i in range(0,len(yvec)):
            for j in range(0,len(qvec)):
                cdt = str(yvec[i]) + "-" + mvec[j] + "-" + dvec[j]
                if cdt <= "2022-12-31":
                    the_dates.append( mvec[j] + dvec[j] + str(yvec[i]))
        self.the_idates = the_dates
        
    def generate_file_ddates(self,ddt_start,ddt_end):
        yvec = range(int(self.get_ddt_yr(ddt_start)),int(self.get_ddt_yr(ddt_end)))
        dvec = ["31","30","30","31"]
        mvec = ["03","06","09","12"]
        qvec = ["03-31","06-30","09-30","12-31"]
        yvec = range(int(self.ddt_start[0:4]),int(self.ddt_end[0:4])+1)
        the_dates = []
        for i in range(0,len(yvec)):
            for j in range(0,len(qvec)):
                cdt = str(yvec[i]) + "-" + mvec[j] + "-" + dvec[j]
                if cdt <= "2022-12-31":
                    the_dates.append(cdt)
        self.the_ddates = the_dates    
    
    def convert_file_date_to_ddt(self,file_date):
        #assumes date of form mmddyyyy
        mm = file_date[0:2]
        dd = file_date[2:4]
        yy = file_date[4:8]
        return(yy+"-"+mm+"-"+dd)
    
    def set_data_types(self):
        mnemonics = self.mnemonics
        for i in range(0,len(mnemonics)):
            if mnemonics[i] not in ["RCOA7204", "RCFA7204"]:
                self.all_data[mnemonics[i]] = self.all_data[mnemonics[i]].apply(pd.to_numeric, errors='coerce').fillna(0, downcast='infer')
            else:
                self.all_data[mnemonics[i]] = self.all_data[mnemonics[i]].str.rstrip("%")
                self.all_data[mnemonics[i]] = self.all_data[mnemonics[i]].apply(pd.to_numeric, errors='coerce').fillna(0, downcast='infer')/100

    def create_cr_variables(self,config_pth_fn,the_sheet_name):
        temp_config = pd.read_excel(config_pth_fn,sheet_name = the_sheet_name,keep_default_na=False)
        for i in range(0,len(temp_config)):
            temp_var_nm = temp_config.iloc[i,0]
            temp_var1   = temp_config.iloc[i,1]
            temp_var2   = temp_config.iloc[i,2]
            
            if(temp_var2 == ""):
                self.all_data[temp_var_nm] = self.all_data[temp_var1]
            else:
                if(temp_var_nm == "htm_AOCI"):
                    self.all_data[temp_var_nm] = np.where(np.abs(self.all_data[temp_var1]) > np.abs(self.all_data[temp_var2]), np.abs(self.all_data[temp_var1]),np.abs(self.all_data[temp_var2]))
                else:
                    self.all_data[temp_var_nm] = np.where(self.all_data[temp_var1] > self.all_data[temp_var2], self.all_data[temp_var1],self.all_data[temp_var2])