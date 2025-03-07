# Build and test docker files

Build the `risk-prediction:0.1` image:

```
docker build -t risk-prediction:0.1 -f ./kubernetes/Dockerfile .
```

# Using Airflow

## Install Prerequisites

### Optional: Load custom image (if running locally)

```shell
docker build -t docker.stackable.tech/gaia-x/marispacex-uc2/risk-prediction:0.1 -f ./kubernetes/Dockerfile .
docker push docker.stackable.tech/gaia-x/marispacex-uc2/risk-prediction:0.1

# optional, as the pod template will pull the image if necessary
kind load docker-image docker.stackable.tech/gaia-x/marispacex-uc2/risk-prediction:0.1 -n stackable-data-platform
```

### Create the namespace and the Airflow dependencies

```shell
export NAMESPACE=uc2-riskpred
kubectl create namespace $NAMESPACE
stackablectl op in commons secret airflow

helm repo add bitnami https://charts.bitnami.com/bitnami

helm install -n $NAMESPACE --wait airflow-postgresql bitnami/postgresql --version 12.1.5 \
--set auth.username=airflow \
--set auth.password=airflow \
--set auth.database=airflow

helm install -n $NAMESPACE --wait airflow-redis bitnami/redis \
--set auth.password=redis \
--version 17.3.7 \
--set replica.replicaCount=1
```

## Create S3 buckets

This has the advantage of keeping all business logic out of the images, which means they could be hosted publically.

Setup up Minio:

```shell
kubectl -n $NAMESPACE apply -f ./kubernetes/s3-secret.yaml

helm install airflow-minio \
--namespace $NAMESPACE \
--version 14.6.16 \
-f ./kubernetes/minio-values.yaml \
--repo https://charts.bitnami.com/bitnami minio

kubectl -n $NAMESPACE apply -f ./kubernetes/minio-client.yaml
```

## Deploy Airflow cluster

Deploy airflow cluster with ConfigMap scripts:

```shell
kubectl -n $NAMESPACE apply -f ./kubernetes/pvc.yaml
kubectl -n $NAMESPACE apply -f ./kubernetes/airflow.yaml
kubectl -n $NAMESPACE apply -f ./kubernetes/auth-class.yaml
```

Copy model dependencies directly to pvc-mount of the single airflow worker, thus keeping all model resources private:

```shell
tar -cvf - ./code | kubectl -n $NAMESPACE exec airflow-worker-default-0 --container=airflow -i -- tar -xvf - --exclude='./code/data/data' --strip-components=1 --no-same-owner --no-same-permissions --directory=/tmp
```

# REST Endpoints

## Minio and Airflow

```shell
export NAMESPACE=uc2-riskpred
MINIO_POD=$(kubectl -n $NAMESPACE get pod -l app.kubernetes.io/instance=airflow-minio -o name | head -n 1 | sed -e 's#pod/##')
MINIO_HOST=$(kubectl -n $NAMESPACE get pod $MINIO_POD -o yaml | yq -e '.status.hostIP')
MINIO_PORT=$(kubectl -n $NAMESPACE get service airflow-minio -o yaml | yq -e '.spec.ports[] | select (.name == "minio-console") | .nodePort')
export MINIO_URL=$MINIO_HOST:$MINIO_PORT
echo 'Minio reachable at:' $MINIO_URL

AIRFLOW_HOST=$(kubectl -n $NAMESPACE get pod airflow-worker-default-0 -o yaml | yq -e '.status.hostIP')
AIRFLOW_PORT=$(kubectl -n $NAMESPACE get service airflow-webserver -o yaml | yq -e '.spec.ports[].nodePort')
export AIRFLOW_URL=$AIRFLOW_HOST:$AIRFLOW_PORT
echo 'Airflow reachable at:' $AIRFLOW_URL
```

# Run models

Prepare buckets for initial run:

```shell
export NAMESPACE=uc2-riskpred
export MINIO_CLIENT=$(kubectl -n $NAMESPACE get pod -l app=minio-client -o name | head -n 1 | sed -e 's#pod/##')
kubectl exec -n $NAMESPACE $MINIO_CLIENT -- sh -c 'mc alias set airflow-minio http://airflow-minio:9000 $MINIO_SERVER_ACCESS_KEY $MINIO_SERVER_SECRET_KEY'
kubectl exec -n $NAMESPACE $MINIO_CLIENT -- mc mb airflow-minio/riskpred-output
```