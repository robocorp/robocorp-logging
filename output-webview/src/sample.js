export function getSampleContents() {
    return "V 1\nT 2023-03-30T11:51:26.518\nID 1|0e3856cc-ced8-11ed-8c8b-a683e7bfc008\nI \"sys.platform=darwin\"\nI \"python=3.9.13 | packaged by conda-forge | (main, May 27 2022, 17:01:00) \\n[Clang 13.0.1 ]\"\nM a:\"challenge\"\nM b:\"/Users/jau/Desktop/robocorp/poc-python-rpa-robot-structure-master/rpa-challenge/challenge.py\"\nSS a|a|b|2.206\nM c:\"run\"\nM d:\"challenge.run\"\nST c|d|59|2.207\nM e:\"\"\nM f:\"METHOD\"\nSK c|e|f|e|b|60|2.207\nM g:\"start_the_challenge\"\nSK g|e|f|e|b|37|2.207\nM h:\"PASS\"\nM S:\"ERROR\"\nEK h|10.791\nM i:\"fill_the_forms\"\nSK i|e|f|e|b|45|10.791\nM j:\"get_the_list_of_people_from_the_excel_file\"\nSK j|e|f|e|b|9|10.791\nEK h|10.911\nM k:\"fill_and_submit_the_form\"\nSK k|e|f|e|b|22|10.911\nM l:\"person={'First Name': 'John', 'Last Name': 'Smith', 'Company Name': 'IT Solutions', 'Role in Company': 'Analyst', 'Address': '98 North Road', 'Email': 'jsmith@itsolutions.co.uk', 'Phone Number': 40716543298}\"\nKA l\nM m:\"set_value_by_xpath\"\nSK m|e|f|e|b|17|10.911\nM n:\"xpath='//input[@ng-reflect-name=\\\"labelFirstName\\\"]'\"\nKA n\nM o:\"value='John'\"\nKA o\nEK h|10.915\nSK m|e|f|e|b|17|10.915\nM p:\"xpath='//input[@ng-reflect-name=\\\"labelLastName\\\"]'\"\nKA p\nM q:\"value='Smith'\"\nKA q\nEK h|10.918\nSK m|e|f|e|b|17|10.918\nM r:\"xpath='//input[@ng-reflect-name=\\\"labelCompanyName\\\"]'\"\nKA r\nM s:\"value='IT Solutions'\"\nKA s\nEK h|10.921\nSK m|e|f|e|b|17|10.921\nM t:\"xpath='//input[@ng-reflect-name=\\\"labelRole\\\"]'\"\nKA t\nM u:\"value='Analyst'\"\nKA u\nEK h|10.924\nSK m|e|f|e|b|17|10.924\nM v:\"xpath='//input[@ng-reflect-name=\\\"labelAddress\\\"]'\"\nKA v\nM w:\"value='98 North Road'\"\nKA w\nEK h|10.927\nSK m|e|f|e|b|17|10.927\nM x:\"xpath='//input[@ng-reflect-name=\\\"labelEmail\\\"]'\"\nKA x\nM y:\"value='jsmith@itsolutions.co.uk'\"\nKA y\nEK h|10.93\nSK m|e|f|e|b|17|10.93\nM z:\"xpath='//input[@ng-reflect-name=\\\"labelPhone\\\"]'\"\nKA z\nM A:\"value=40716543298\"\nKA A\nEK h|10.933\nEK h|10.975\nSK k|e|f|e|b|22|10.975\nM B:\"person={'First Name': 'Jane', 'Last Name': 'Dorsey', 'Company Name': 'MediCare', 'Role in Company': 'Medical Engineer', 'Address': '11 Crown Street', 'Email': 'jdorsey@mc.com', 'Phone Number': 40791345621}\"\nKA B\nSK m|e|f|e|b|17|10.975\nKA n\nM C:\"value='Jane'\"\nKA C\nEK h|10.978\nSK m|e|f|e|b|17|10.978\nKA p\nM D:\"value='Dorsey'\"\nKA D\nEK h|10.981\nSK m|e|f|e|b|17|10.981\nKA r\nM E:\"value='MediCare'\"\nKA E\nEK h|10.984\nSK m|e|f|e|b|17|10.984\nKA t\nM F:\"value='Medical Engineer'\"\nKA F\nEK h|10.988\nSK m|e|f|e|b|17|10.988\nKA v\nM G:\"value='11 Crown Street'\"\nKA G\nEK h|10.991\nSK m|e|f|e|b|17|10.991\nKA x\nM H:\"value='jdorsey@mc.com'\"\nKA H\nEK h|10.994\nSK m|e|f|e|b|17|10.994\nKA z\nM I:\"value=40791345621\"\nKA I\nEK h|10.997\nEK h|11.024\nSK k|e|f|e|b|22|11.025\nM J:\"person={'First Name': 'Albert', 'Last Name': 'Kipling', 'Company Name': 'Waterfront', 'Role in Company': 'Accountant', 'Address': '22 Guild Street', 'Email': 'kipling@waterfront.com', 'Phone Number': 40735416854}\"\nKA J\nSK m|e|f|e|b|17|11.025\nKA n\nM K:\"value='Albert'\"\nKA K\nEK h|11.029\nSK m|e|f|e|b|17|11.029\nKA p\nM L:\"value='Kipling'\"\nKA L\nEK h|11.032\nSK m|e|f|e|b|17|11.032\nKA r\nM M:\"value='Waterfront'\"\nKA M\nEK h|11.035\nSK m|e|f|e|b|17|11.035\nKA t\nM N:\"value='Accountant'\"\nKA N\nEK h|11.039\nSK m|e|f|e|b|17|11.039\nKA v\nM O:\"value='22 Guild Street'\"\nKA O\nEK h|11.042\nSK m|e|f|e|b|17|11.042\nKA x\nM P:\"value='kipling@waterfront.com'\"\nKA P\nEK h|11.045\nSK m|e|f|e|b|17|11.045\nKA z\nM Q:\"value=40735416854\"\nKA Q\nEK h|11.048\nEK h|11.076\nSK k|e|f|e|b|22|11.076\nM R:\"person=None\"\nKA R\nEK S|11.076\nEK S|11.076\nEK S|11.076\nET S|e|11.077\nES S|11.077\n";
}