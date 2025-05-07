# OpenShift Deployment Guide for Vectorization Service

This guide explains how to deploy the Vectorization Service on Red Hat OpenShift.

## Overview

OpenShift is Red Hat's enterprise Kubernetes platform with additional security features and built-in CI/CD capabilities. The key differences for deploying our service on OpenShift include:

1. Using OpenShift `Route` instead of Kubernetes `Ingress`
1. Adapting security contexts for OpenShift's stricter security model
1. Utilizing OpenShift's integrated image building capabilities

## Prerequisites

- Access to an OpenShift cluster (v4.x recommended)
- The `oc` command-line tool installed and configured
- Permissions to create resources in at least one namespace

## Step 1: Create a New Project

```bash
oc new-project vectorization-service
```

## Step 2: Configure Image Streams and Build Configs

First, create the ImageStream:

```bash
oc apply -f imagestream.yaml
```

Then configure the build process:

```bash
# Update the Git repository URL in buildconfig.yaml before running this
oc apply -f buildconfig.yaml
```

You can start a build with:

```bash
oc start-build vectorization-service
```

## Step 3: Deploy the Application Components

Apply the main deployment configuration:

```bash
oc apply -f deployment.yaml
```

Apply the horizontal pod autoscaler:

```bash
oc apply -f hpa.yaml
```

## Step 4: Verify the Deployment

Check if pods are running:

```bash
oc get pods
```

Check the route that was created:

```bash
oc get routes
```

Access your service using the hostname provided by the route.

## Step 5: Configure Security

### Service Account and Role Binding

If your service needs specific permissions, create a service account:

```bash
oc create serviceaccount vectorization-sa
oc policy add-role-to-user view -z vectorization-sa
```

Update your deployment to use this service account:

```yaml
spec:
  template:
    spec:
      serviceAccountName: vectorization-sa
```

### Security Context Constraints (SCC)

If you need additional permissions:

```bash
oc adm policy add-scc-to-user anyuid -z vectorization-sa
```

Note: Try to avoid using `anyuid` in production; it's better to adapt your container to work with random UIDs.

## Step 6: Configure Resource Quotas and Limits

Set namespace limits:

```bash
oc apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: vectorization-quota
spec:
  hard:
    pods: "20"
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "16"
    limits.memory: 32Gi
EOF
```

## Step 7: Set Up Monitoring

Enable monitoring for your project:

```bash
oc apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: vectorization-monitor
  labels:
    k8s-app: vectorization-service
spec:
  selector:
    matchLabels:
      app: vectorization-service
  endpoints:
  - port: http
    interval: 30s
EOF
```

## Troubleshooting

### Pod won't start or crashes

Check pod details:

```bash
oc describe pod <pod-name>
```

View logs:

```bash
oc logs <pod-name>
```

### Image pull issues

Check build logs:

```bash
oc logs -f bc/vectorization-service
```

### Route not accessible

Check route status:

```bash
oc describe route vectorization-service
```

Verify the service is running:

```bash
oc get endpoints vectorization-service
```

## Advanced Configuration

### Enable HTTPS with Custom Certificates

Update your route configuration:

```bash
oc patch route vectorization-service -p '{"spec":{"tls":{"termination":"edge","certificate":"'"$(cat cert.pem)"'","key":"'"$(cat key.pem)"'"}}}'
```

### Configure Network Policies

Create a network policy to restrict traffic:

```bash
oc apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
spec:
  podSelector: {}
  ingress:
  - from:
    - podSelector: {}
EOF
```

## CI/CD Integration

OpenShift provides built-in CI/CD capabilities. You can set up a webhook in your Git repository to trigger automatic builds whenever changes are pushed.

Update your BuildConfig with a webhook trigger:

```bash
WEBHOOK_SECRET=$(oc get bc/vectorization-service -o jsonpath='{.spec.triggers[?(@.github)].github.secret}')
WEBHOOK_URL=$(oc describe bc/vectorization-service | grep -A 1 "Webhook GitHub" | tail -1 | awk '{print $2}')

echo "GitHub webhook URL: $WEBHOOK_URL"
echo "Secret: $WEBHOOK_SECRET"
```

Configure this webhook in your GitHub repository settings.

## Scaling and Performance Tuning

The HorizontalPodAutoscaler will handle automatic scaling based on CPU and memory usage. You may want to adjust the thresholds based on observed usage patterns.

For performance tuning:

1. Monitor actual CPU/memory usage with the OpenShift dashboard
2. Adjust resource requests/limits accordingly
3. Consider using node selectors to place pods on appropriate hardware
4. Optimize the number of Gunicorn workers based on your CPU configuration