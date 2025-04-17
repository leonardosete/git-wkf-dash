# gt-dash Helm Chart & Deploy Automation

Este repositório contém o Helm Chart do **GitHub Actions Dashboard (`gt-dash`)** e o processo completo de deploy automatizado via **GitHub Actions + Ansible + ArgoCD**.

---

## 📦 Estrutura do Repositório

```bash
kind-cluster-n8n/
├── .github/workflows/
│   └── git-actions-apply-argo-apps.yaml   # Workflow do GitHub Actions
├── ansible-hostinger/
│   ├── inventory.ini
│   └── ansible-apply-argo-apps.yml        # Playbook Ansible
├── argo-apps/
│   └── gt-dash-helm.yaml                  # Application do ArgoCD
├── apps/
│   └── gt-dash-helm/                      # Helm Chart do gt-dash
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── secrets/
│   └── gt-dash-secret.yaml.j2             # Template Jinja2 do Secret
```

---

## 🚀 Visão Geral do Processo

1. Commit/push para `main` ou trigger manual (`workflow_dispatch`)
2. GitHub Actions faz SSH na VPS
3. Copia os manifests e templates para a VPS
4. Executa o Ansible:
   - Aplica Secret `gt-dash-secret` se ainda não existir
   - Aplica os Applications ArgoCD se ainda não existirem
   - Aguarda sincronização completa com `argocd app wait`

---

## 🔐 Segredos no GitHub

Você precisa criar os seguintes **Secrets** no repositório GitHub:

| Nome               | Descrição                        |
|--------------------|----------------------------------|
| `GH_DASH_TOKEN`    | Token fine-grained do GitHub     |
| `SSH_PRIVATE_KEY`  | Chave privada SSH para acessar VPS |

E os seguintes **Variables**:

| Nome               | Exemplo                         |
|--------------------|----------------------------------|
| `VPS_HOSTNAME`     | `meu-servidor.com`              |
| `VPS_USER`         | `root`                          |
| `SSH_KEY_FILENAME` | `id_rsa`                        |

---

## 🗂️ Valores do Chart

No `values.yaml`, mantemos apenas variáveis **públicas** como o nome do repositório monitorado:

```yaml
publicRepos: leonardosete/kind-cluster-n8n
```

O valor do token GitHub (`GITHUB_TOKEN`) é fornecido via Secret dinâmico gerado pelo Ansible.

---

## 📦 Helm Install Manual (opcional)

Se quiser instalar manualmente o chart:

```bash
helm upgrade --install gt-dash apps/gt-dash-helm \
  -n gt-dash-helm --create-namespace \
  -f apps/gt-dash-helm/values.yaml
```

---

## ✅ Pronto!

Esse fluxo garante deploy seguro e automatizado com GitOps, com proteção a segredos sensíveis e observabilidade via ArgoCD.

Se quiser extender isso para múltiplos ambientes (dev/staging/prod), podemos modularizar com Helm + Kustomize + ArgoCD Projects. Só pedir! 🚀
