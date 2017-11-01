cd
pushd .
call "C:\Program Files (x86)\Google\Cloud SDK\cloud_env.bat"
popd
cd ..
cd 17Z_search
gcloud app deploy app.yaml --project zsearch1 -v 2
cd ..
cd 17Z
gcloud app deploy --project zflexible1 -v 1
