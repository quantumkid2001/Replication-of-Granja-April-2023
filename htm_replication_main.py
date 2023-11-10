# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 11:47:14 2023

@author: quantumkid
"""
from Model_Mngr import Model_Mngr
import pandas as pd
import numpy as np

config_file = "C:\\work\\frbsf_code_sample\\inputs\\cr_variable_list_hfs_afs_comp.xlsx"
the_model_mngr = Model_Mngr(config_file,"2021-03-31","2022-12-31","composite_vars","model_vars","shift_vars","shf_mdl_vars")
the_model_mngr.construct_model_vars()
the_model_mngr.construct_shift_vars()
the_model_mngr.construct_shift_model_vars()
the_model_mngr.construct_asset_percentile_rank()
the_model_mngr. set_model_criteria_1()
the_model_mngr. set_model_criteria_2()

the_model_mngr.create_figure_1()
the_model_mngr.create_figure_2()
the_model_mngr.create_figure_3()
the_model_mngr.create_figure_4()

print(the_model_mngr.create_regression_panel_a_1())
print(the_model_mngr.create_regression_panel_a_2())
print(the_model_mngr.create_regression_panel_a_3())
print(the_model_mngr.create_regression_panel_a_4())

test = the_model_mngr.the_data_mngr.all_data

subtest = test[test["ddt"] == '2021-03-31']

the_trans_banks = test[test["meets_both"] == 1]
rssd_both = the_trans_banks.IDRSSD.unique()

subtest["met_both"] = np.where(subtest["IDRSSD"].isin(rssd_both), 1,0)
subtest = subtest[~subtest["IDRSSD"].isna()]

min_lr = min(subtest["lev_ratio"])
max_lr = max(subtest["lev_ratio"])

subtest["lev_ratio"].hist(weights=np.ones(len(subtest)) / len(subtest), bins=20, stacked=False, alpha=.5)
subsubtest = subtest[subtest["met_both"] == 1]
counts, bins, bars = subsubtest["lev_ratio"].hist(weights=np.ones(len(subsubtest)) / len(subsubtest), bins=20, stacked=False, alpha=.5)
pd.cut(subsubtest['lev_ratio'], 20).value_counts().sort_index()
# test["c1_sec_trans"] = np.where(test["meets_c1"] == 1,test["sec_trans"],0)
# test["c2_sec_trans"] = np.where((test["meets_c1"] == 0) & (test["meets_c2"] == 1),test["sec_trans"],0)

# the_table = pd.pivot_table(data=test,index=['ddt'],values=['c1_sec_trans','c2_sec_trans'],aggfunc=np.sum)
# the_table = the_table.cumsum()
# the_table = the_table.sort_index(ascending=False)
# the_table.plot(kind='barh',stacked=True,title="Figure 3: Cumulative amounts reclassified into HTM by quarter")
