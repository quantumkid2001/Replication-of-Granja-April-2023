# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 16:26:21 2023

@author: quantumkid
"""
import statsmodels.formula.api as smf
from Data_Mngr import Data_Mngr
import pandas as pd
import numpy as np
import pylab as pl

class Model_Mngr:
    def __init__(self,config_file,s_ddt, e_ddt,cmpst_sht_name,mdl_sht_name,shf_sht_name,shf_mdl_sht_name):
        self.the_data_mngr = Data_Mngr(config_file,s_ddt,e_ddt)
        self.the_data_mngr.create_full_data_set()
        self.the_data_mngr.set_data_types()
        self.the_data_mngr.create_cr_variables(config_file,cmpst_sht_name)
        self.model_vars = pd.read_excel(config_file,sheet_name=mdl_sht_name,keep_default_na = False)
        self.shift_vars = pd.read_excel(config_file,sheet_name=shf_sht_name,keep_default_na = False)
        self.shift_model_vars = pd.read_excel(config_file,sheet_name=shf_mdl_sht_name,keep_default_na = False)
    
    def construct_shift_vars(self):
        #print("constructing shift vars")
        for i in range(0,len(self.shift_vars)):
            the_var = self.shift_vars.iloc[i,0]
            shift_var = "p_" + self.shift_vars.iloc[i,0]
            self.the_data_mngr.all_data[shift_var] = self.the_data_mngr.all_data.groupby('IDRSSD')[the_var].shift()
    
    def construct_model_vars(self):
        #print("constructing model vars")
        for i in range(0,len(self.model_vars)):
            temp_var = self.model_vars.iloc[i,0]
            temp_eq  = self.model_vars.iloc[i,1]
            eval_str = temp_var + " = " + temp_eq
            #print(temp_var)
            self.the_data_mngr.all_data = self.the_data_mngr.all_data.eval(eval_str)
            
    def construct_shift_model_vars(self):
        #print("constructing shift model vars")
        self.the_data_mngr.all_data = self.the_data_mngr.all_data.sort_values(by=['IDRSSD','ddt'])
        for i in range(0,len(self.shift_model_vars)):
            temp_var = self.shift_model_vars["var"].iloc[i]
            temp_eq  = self.shift_model_vars["equation"].iloc[i]
            eval_str = temp_var + " = " + temp_eq
            #print(temp_var)
            self.the_data_mngr.all_data = self.the_data_mngr.all_data.eval(eval_str)
     
    def construct_asset_percentile_rank(self):
        self.the_data_mngr.all_data = self.the_data_mngr.all_data.assign(percentile=self.the_data_mngr.all_data.groupby("ddt")["tot_assets"].rank(pct=True))
        self.the_data_mngr.all_data["qtr1"] = np.where(self.the_data_mngr.all_data["percentile"] < .25, 1, 0)
        self.the_data_mngr.all_data["qtr2"] = np.where((self.the_data_mngr.all_data["percentile"] >= .25) & (self.the_data_mngr.all_data["percentile"] < .5), 1, 0)
        self.the_data_mngr.all_data["qtr3"] = np.where((self.the_data_mngr.all_data["percentile"] >= .5) & (self.the_data_mngr.all_data["percentile"] < .75), 1, 0)
        self.the_data_mngr.all_data["qtr4"] = np.where(self.the_data_mngr.all_data["percentile"] >= .75, 1, 0)
        pass
    
    def set_model_criteria_1(self):
        #c1a.  "Increase in the amortized cost of held-to-maturity securities that exceeds 15% of the total
        #amortized cost of AFS and HTM securities in the previous quarter,"
        #large change in htm relative to last qtr
        #this qtr's htm is larger than last's and that delta is > 15% of last period total ac sec
        #test["ratio_c1a"] = (test["htm_ac"] - test["p_htm_ac"])/(test["p_tot_sec_ac"])
        self.the_data_mngr.all_data["c1a"] = np.where(self.the_data_mngr.all_data["ratio_c1a"] > 0.15, 1, 0)

        #c1b.  "Increase in the sum of the amortized costs of held-to-maturity and available for sale securities
        #that does not exceed 7.5% of the total amortized cost of AFS and HTM securities in the
        #previous quarter, and"
        #overall change in htm and afs is limited
        #test["ratio_c1b"] = (test["tot_sec_ac"] - test["p_tot_sec_ac"])/test["p_tot_sec_ac"]
        self.the_data_mngr.all_data["c1b"] = np.where(self.the_data_mngr.all_data["ratio_c1b"] <= 0.075,1,0)

        #c1c.  a non-zero change in the absolute value of the net unrealized gains (losses) on held-to-maturity
        #securities that are included in Accumulated Other Comprehensive Income (AOCI)
        self.the_data_mngr.all_data["c1c"] = np.where(self.the_data_mngr.all_data["htm_AOCI"] > 0, 1, 0)
        self.the_data_mngr.all_data["meets_c1"] = np.where(self.the_data_mngr.all_data["RCOAP838"] == 1,  self.the_data_mngr.all_data["c1a"] *  self.the_data_mngr.all_data["c1b"] *  self.the_data_mngr.all_data["c1c"],  self.the_data_mngr.all_data["c1a"] *  self.the_data_mngr.all_data["c1b"])
    
    def set_model_criteria_2(self):
        #Increase in the amortized cost of held-to-maturity securities that exceeds 5% of the total
        #amortized cost of AFS and HTM securities in the previous quarter,
        self.the_data_mngr.all_data["c2a"] = np.where(self.the_data_mngr.all_data["ratio_c1a"] > .05, 1, 0)

        #Increase in the sum of the amortized cost of held-to-maturity and available for sale securities
        #that does not exceed 2.5% of the total amortized cost of AFS and HTM securities in the
        #previous quarter, and
        self.the_data_mngr.all_data["c2b"] = np.where(self.the_data_mngr.all_data["ratio_c1b"] <= 0.025, 1,0)

        #An absolute change in the absolute value of the net unrealized gains (losses) on held-to-maturity
        #securities that are included in Accumulated Other Comprehensive Income (AOCI) that exceeds
        #0.25% of the total amortized cost of AFS and HTM securities in the previous quarte
        self.the_data_mngr.all_data["c2c"] = np.where(np.abs( self.the_data_mngr.all_data["htm_AOCI"]-self.the_data_mngr.all_data["p_htm_AOCI"])/ self.the_data_mngr.all_data["p_tot_sec_ac"] > 0.0025,1,0)
        self.the_data_mngr.all_data["meets_c2"] = np.where( self.the_data_mngr.all_data["RCOAP838"] == 1,  self.the_data_mngr.all_data["c2a"] *  self.the_data_mngr.all_data["c2b"] *  self.the_data_mngr.all_data["c2c"],  self.the_data_mngr.all_data["c2a"] *  self.the_data_mngr.all_data["c2b"])

    def create_figure_1(self):
        #self.the_data_mngr.all_data["tot_sec"] = np.where(self.the_data_mngr.all_data["meets_c1"] > self.the_data_mngr.all_data["meets_c2"], self.the_data_mngr.all_data["meets_c1"], self.the_data_mngr.all_data["meets_c2"])
        the_table = pd.pivot_table(data=self.the_data_mngr.all_data,index=['ddt'],values=["afs_fv","htm_ac"],aggfunc=np.sum)
        the_table = the_table.sort_index(ascending=False)
        the_table.plot(kind='barh',stacked=False,title="Figure 1: Breakdown of Total Securities held by US Banks")
        pass
    
    def create_figure_2(self):
        self.the_data_mngr.all_data["meets_both"] = np.where(self.the_data_mngr.all_data["meets_c1"] > self.the_data_mngr.all_data["meets_c2"], self.the_data_mngr.all_data["meets_c1"], self.the_data_mngr.all_data["meets_c2"])
        the_table = pd.pivot_table(data=self.the_data_mngr.all_data,index=['ddt'],values=["meets_c1","meets_c2","meets_both"],aggfunc=np.sum)
        the_table.plot(style=['--bo','--rx','--g*'],rot=45, title="Figure 2: Number of Banks reclassifying securities by quarter",ylim=[0,60])
    
    def create_figure_3(self):
        self.the_data_mngr.all_data["sec_trans"] = np.where(self.the_data_mngr.all_data["meets_both"] > 0, self.the_data_mngr.all_data["htm_ac"] - self.the_data_mngr.all_data["p_htm_ac"],0)
        self.the_data_mngr.all_data["c1_sec_trans"] = np.where(self.the_data_mngr.all_data["meets_c1"] == 1,self.the_data_mngr.all_data["sec_trans"],0)
        self.the_data_mngr.all_data["c2_sec_trans"] = np.where((self.the_data_mngr.all_data["meets_c1"] == 0) & (self.the_data_mngr.all_data["meets_c2"] == 1),self.the_data_mngr.all_data["sec_trans"],0)

        the_table = pd.pivot_table(data=self.the_data_mngr.all_data,index=['ddt'],values=['c1_sec_trans','c2_sec_trans'],aggfunc=np.sum)
        the_table = the_table.cumsum()
        the_table = the_table.sort_index(ascending=False)
        the_table.plot(kind='barh',stacked=True,title="Figure 3: Cumulative amounts reclassified into HTM by quarter")

    def create_figure_4(self):
        the_trans_banks = self.the_data_mngr.all_data[self.the_data_mngr.all_data["meets_both"] == 1]
        rssd_both = the_trans_banks.IDRSSD.unique()
        data_both = self.the_data_mngr.all_data[self.the_data_mngr.all_data["IDRSSD"].isin(rssd_both)]
        sec_trans_df = pd.pivot_table(data=data_both,index=['IDRSSD'],values=['sec_trans'],aggfunc=np.sum)
        sec_trans_df.columns=["tot_sec_trans"]
        sec_total_both = data_both[data_both["ddt"] == '2022-12-31']
        sec_total_both = sec_total_both.set_index("IDRSSD")
        all_sec_total_data = sec_trans_df.merge(sec_total_both, how='inner', left_index=True, right_index=True)
        all_sec_total_data["sec_ratio"] = all_sec_total_data["tot_sec_trans"]/all_sec_total_data["htm_ac"]
        all_sec_total_data = all_sec_total_data.replace([np.inf, -np.inf], np.nan)
        all_sec_total_data = all_sec_total_data.dropna(subset=['sec_ratio'])
        all_sec_total_data.hist("sec_ratio",weights=np.ones(len(all_sec_total_data)) / len(all_sec_total_data), bins=20, stacked=False, alpha=.5)
        pl.suptitle("Figure 4: Histogram of amounts reclassified as a % of HTM securities at the end of 2022")
        
    def create_figure_5a(self):
        
        pass
    
    def create_figure_5b(self):
        
        pass
    
    def create_figure_5c(self):
        
        pass
    
    def create_figure_5d(self):
        
        pass
    
    def create_regression_panel_a_1(self):
        the_trans_banks = self.the_data_mngr.all_data[self.the_data_mngr.all_data["meets_both"] == 1]
        rssd_both = the_trans_banks.IDRSSD.unique()
        
        subtest =  self.the_data_mngr.all_data[ self.the_data_mngr.all_data["ddt"] == "2021-03-31"]
        subtest["met_both"] = np.where(subtest["IDRSSD"].isin(rssd_both), 1,0)
        subtest = subtest[~subtest["IDRSSD"].isna()]
        
        df_regress = subtest
        avg = df_regress['lev_ratio'].mean()
        std = df_regress['lev_ratio'].std()
        df_regress['z_lev_ratio'] = ((df_regress['lev_ratio']-avg)/std)
        model = smf.ols(formula='met_both ~ z_lev_ratio + qtr1 + qtr2 + qtr3', data=df_regress).fit()
        
        with open("C:\\work\\frbsf_code_sample\\output\\panel_a_1.txt", 'w') as fh:
            fh.write(model.summary().as_text())
        return(model.summary())
     
    def create_regression_panel_a_2(self):
        the_trans_banks = self.the_data_mngr.all_data[self.the_data_mngr.all_data["meets_both"] == 1]
        rssd_both = the_trans_banks.IDRSSD.unique()
        
        subtest =  self.the_data_mngr.all_data[ self.the_data_mngr.all_data["ddt"] == "2021-03-31"]
        subtest["met_both"] = np.where(subtest["IDRSSD"].isin(rssd_both), 1,0)
        subtest = subtest[~subtest["IDRSSD"].isna()]
        
        df_regress = subtest
        fdic_banks = self.the_data_mngr.get_fdic_data("03312021")
        qbr_banks = self.the_data_mngr.get_fdic_qbr_info_file("03312021")
        qbr_banks = qbr_banks[["IDRSSD","FDIC Certificate Number"]]
        qbr_banks = qbr_banks.rename(columns={"IDRSSD":"IDRSSD","FDIC Certificate Number":"cert"})

        #########uninsured dep regression###########
        idrssd_qbr_banks = pd.merge(fdic_banks, qbr_banks, on='cert', how='outer')
        idrssd_qbr_banks = idrssd_qbr_banks[idrssd_qbr_banks["class"] != "OI"]
        idrssd_qbr_banks = idrssd_qbr_banks[~idrssd_qbr_banks["class"].isna()]

        df_regress = df_regress[df_regress["IDRSSD"].isin(idrssd_qbr_banks["IDRSSD"])]
        avg = df_regress['un_dep_shr'].mean()
        std = df_regress['un_dep_shr'].std()
        df_regress['z_un_dep_shr'] = ((df_regress['un_dep_shr']-avg)/std)
        model = smf.ols(formula='met_both ~ z_un_dep_shr + qtr3 + qtr4 - 1', data=df_regress).fit()
        
        with open('C:\\work\\frbsf_code_sample\\output\\panel_a_2.txt', 'w') as fh:
            fh.write(model.summary().as_text())
        return(model.summary())

    def create_regression_panel_a_3(self):
        the_trans_banks = self.the_data_mngr.all_data[self.the_data_mngr.all_data["meets_both"] == 1]
        rssd_both = the_trans_banks.IDRSSD.unique()
        
        subtest =  self.the_data_mngr.all_data[ self.the_data_mngr.all_data["ddt"] == "2021-03-31"]
        subtest["met_both"] = np.where(subtest["IDRSSD"].isin(rssd_both), 1,0)
        subtest = subtest[~subtest["IDRSSD"].isna()]

        df_regress = subtest
        df_regress = df_regress[~df_regress["long_shr"].isna()]
        avg = df_regress['long_shr'].mean()
        std = df_regress['long_shr'].std()
        df_regress['z_long_shr'] = ((df_regress['long_shr']-avg)/std)
        model = smf.ols(formula='met_both ~ z_long_shr + qtr3 + qtr4 - 1', data=df_regress).fit()
        
        with open('C:\\work\\frbsf_code_sample\\output\\panel_a_3.txt', 'w') as fh:
            fh.write(model.summary().as_text())
        return(model.summary())

    def create_regression_panel_a_4(self):
        the_trans_banks = self.the_data_mngr.all_data[self.the_data_mngr.all_data["meets_both"] == 1]
        rssd_both = the_trans_banks.IDRSSD.unique()
        
        subtest =  self.the_data_mngr.all_data[ self.the_data_mngr.all_data["ddt"] == "2021-03-31"]
        subtest["met_both"] = np.where(subtest["IDRSSD"].isin(rssd_both), 1,0)
        subtest = subtest[~subtest["IDRSSD"].isna()]
        df_regress = subtest
        fdic_banks = self.the_data_mngr.get_fdic_data("03312021")
        qbr_banks = self.the_data_mngr.get_fdic_qbr_info_file("03312021")
        qbr_banks = qbr_banks[["IDRSSD","FDIC Certificate Number"]]
        qbr_banks = qbr_banks.rename(columns={"IDRSSD":"IDRSSD","FDIC Certificate Number":"cert"})

        idrssd_qbr_banks = pd.merge(fdic_banks, qbr_banks, on='cert', how='outer')
        idrssd_qbr_banks = idrssd_qbr_banks[idrssd_qbr_banks["class"] != "OI"]
        idrssd_qbr_banks = idrssd_qbr_banks[~idrssd_qbr_banks["class"].isna()]

        df_regress = df_regress[df_regress["IDRSSD"].isin(idrssd_qbr_banks["IDRSSD"])]
        df_regress = df_regress[~df_regress["long_shr"].isna()]
        avg = df_regress['long_shr'].mean()
        std = df_regress['long_shr'].std()
        df_regress['z_long_shr'] = ((df_regress['long_shr']-avg)/std)

        avg = df_regress['un_dep_shr'].mean()
        std = df_regress['un_dep_shr'].std()
        df_regress['z_un_dep_shr'] = ((df_regress['un_dep_shr']-avg)/std)
        model = smf.ols(formula='met_both ~ z_un_dep_shr + z_long_shr + z_un_dep_shr * z_long_shr + qtr3 + qtr4 - 1', data=df_regress).fit()
        
        with open('C:\\work\\frbsf_code_sample\\output\\panel_a_4.txt', 'w') as fh:
            fh.write(model.summary().as_text())
        return(model.summary())