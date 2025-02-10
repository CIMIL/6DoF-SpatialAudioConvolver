import os
import shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SOFA_HOMEBASE = os.path.abspath(r"D:\develop-farina-proj\MATRICES(hrtf-and-SOFA)\SOFA\createTESTsofa\SOFA_tindari_variants")

templates = {
    'new':{
        16: "template_NEW_5min_16ch.rpp",
        36: "template_NEW_5min_36ch.rpp",
        64: "template_NEW_5min_64ch.rpp",
    },
    'old':{
        16: "template_OLD_5min_16ch.rpp",
        36: "template_OLD_5min_36ch.rpp",
        64: "template_OLD_5min_64ch.rpp",
    },
}

sofas = ['01_16ch_100ms_tindari_drop.sofa',
         '02_16ch_200ms_tindari_drop.sofa',
         '03_16ch_500ms_tindari_drop.sofa',
         '04_16ch_1s_tindari_drop.sofa',
         '05_16ch_2s_tindari_drop.sofa',
         '06_16ch_5s_tindari_drop.sofa',
         '07_16ch_10s_tindari_drop.sofa',
         '08_36ch_100ms_tindari_drop.sofa',
         '09_36ch_200ms_tindari_drop.sofa',
         '10_36ch_500ms_tindari_drop.sofa',
         '11_36ch_1s_tindari_drop.sofa',
         '12_36ch_2s_tindari_drop.sofa',
         '13_36ch_5s_tindari_drop.sofa',
         '14_36ch_10s_tindari_drop.sofa',
         '15_64ch_100ms_tindari_drop.sofa',
         '16_64ch_200ms_tindari_drop.sofa',
         '17_64ch_500ms_tindari_drop.sofa',
         '18_64ch_1s_tindari_drop.sofa',
         '19_64ch_2s_tindari_drop.sofa',
         '20_64ch_5s_tindari_drop.sofa',
         '21_64ch_10s_tindari_drop.sofa']



for k,i in templates.items():
    for k2,i2 in i.items():
        assert type(i2) == str
        assert os.path.exists(i2)
        

for sofa in sofas:
    assert os.path.exists(os.path.join(SOFA_HOMEBASE,sofa))
    sid = sofa.split('_')[0]
    sch = int(sofa.split('_')[1].replace('ch',''))
    print(sid,sch, end=' ')

    for typep in ['NEW','OLD']:
        relative_template = templates[typep.lower()][sch]
        print(relative_template, end='   ')
        new_project_name = str(sid)+"_"+typep+'_ch'+str(sch)+'_'+str(sofa.split('_')[2])+'.rpp'
        # copy with os
        # os.copyfile(relative_template, new_project_name)
        if not os.path.exists(new_project_name):
            shutil.copyfile(relative_template, new_project_name)
            print(new_project_name, end=' ')
        else:
            print("ERROR! Cannot overwrite existing file", end=' ')
        

    print()