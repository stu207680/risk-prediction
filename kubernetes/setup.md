# Build and test docker files

Build the `risk-prediction:0.1` image:

```
docker build -t risk-prediction:0.1 -f ./kubernetes/Dockerfile .
```

# Using Airflow

## Install Prerequisites

### Optional: Load custom image (if running locally)

```shell
docker build -t docker.stackable.tech/gaia-x/marispacex-uc3/risk-prediction:0.1 -f ./kubernetes/Dockerfile .
docker push docker.stackable.tech/gaia-x/marispacex-uc3/risk-prediction:0.1

# optional, as the pod template will pull the image if necessary
kind load docker-image docker.stackable.tech/gaia-x/marispacex-uc3/risk-prediction:0.1 -n stackable-data-platform
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