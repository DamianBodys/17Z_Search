cd
pushd .
call "C:\Program Files (x86)\Google\Cloud SDK\cloud_env.bat"
popd
gcloud app deploy app.yaml --project zsearch1 -v 2
