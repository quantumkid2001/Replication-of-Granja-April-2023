# Replication-of-Granja-April-2023
**Replication of:**  Bank Fragility and Reclassification of Securities into HTM<br />


**URL:**  https://deliverypdf.ssrn.com/delivery.php?ID=956118003098122006115092090107071091003071050014044044030085073074101083110093096002098056127048117058030002097110067013088086038078036073051124093003088003121101024060085053075126081122125003110030086078096082087110001091030003004092118066085093093025&EXT=pdf&INDEX=TRUE<br />


**Last URL Visit:**  11/09/2023<br />


**Assumptions:**  
  1.  Call report data from cdr.ffiec.gov bulk data have been downloaded and extracted and saved in the data dir.
  2.  FDIC Bank data have been downloaded and saved in the fdic data dir.  (https://banks.data.fdic.gov/bankfind-suite/financialreporting)
  3.  Python 3.10 is utilized.

**Directory Structure**<br />
|--C:/<br />
&nbsp;&nbsp;&nbsp;&nbsp;|--work/<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--frbsf_code_sample/<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--data/<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--fdic_data/<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--src/<br />

**Code Files**
1.  htm_replication_main.py:  This is the entry point for running the replication code.  This file resides in the src directory.
2.  Data_Mngr.py:  This code handles the gathering and processing of variable needed for analysis.  The Data_Mngr retrieves call report variables from downloaded ffiec call report data files and processes them acording to information in the configuration file,  cr_variable_list_hfs_afs_comp.xlsx.  This file resides in the src directory.
3.  Model_Mngr.py:  This file constructs model variables based on configurable paramneters as well as hardcoded entries specific to the replication documentation.  This class can be extended to accomdate variant operations if desired.  This file resides in the src directory.
4.  cr_variable_list_hfs_afs_comp.xlsx:  This is a configuration file that defines what raw variables to gather from call report data files (call_vars sheet), combines RCFD and RCON variables to create concept variables (e.g. RCFD2170, RCON2170 equate to total assets) (composite_vars sheet), variables based on equations of composite variables for modeling (model_vars), and lagged variables that need data to be shifted (shift_vars sheet), and finally model variables that need to be shifted (shf_mdl_vars sheet).  This file resides in the input directory.

**Observations**
1.  Able to reproduce figure 1-4
2.  Methodology the author used for Figure 5 has not been replicated.
3.  Regression observations are similar in count.  Betas are same order of magnitude and direction but not exact.

