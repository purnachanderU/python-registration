python-registration/
│
├── .github/
│   └── workflows/
│       └── cicd.yml
│
├── app/
│   └── ...
│
├── Dockerfile
│
├── requirements.txt
│
├── helm/
│   └── python-registration/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-stage.yaml
│       ├── values-prod.yaml
│       │
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── mysql-deployment.yaml
│           ├── mysql-service.yaml
│           ├── mysql-pvc.yaml
│           └── _helpers.tpl
│
└── README.md
