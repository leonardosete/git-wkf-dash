# Nome da imagem
IMAGE_NAME=sevenleo/github-dashboard

# Tag baseada na hora atual (ex: v153012)
IMAGE_TAG := v$(shell date +%H%M%S)

# Diretório com os manifestos
K8S_DIR=./manifesto-k8s

# Exibe a tag gerada
print-tag:
	@echo "📛 Tag gerada: $(IMAGE_TAG)"

# Build com a tag gerada e a tag 'latest'
build:
	docker buildx build --platform linux/amd64 \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		-t $(IMAGE_NAME):latest \
		--push .

# Aguarda a imagem estar disponível no Docker Hub
wait-image:
	@echo "⏳ Verificando disponibilidade da imagem no Docker Hub..."
	@until docker manifest inspect $(IMAGE_NAME):$(IMAGE_TAG) > /dev/null 2>&1; do \
		echo "⏳ Aguardando imagem $(IMAGE_NAME):$(IMAGE_TAG)..."; \
		sleep 5; \
	done
	@until docker manifest inspect $(IMAGE_NAME):latest > /dev/null 2>&1; do \
		echo "⏳ Aguardando imagem $(IMAGE_NAME):latest..."; \
		sleep 5; \
	done
	@echo "✅ Imagens encontradas no Docker Hub!"

## Aplica Redis (se necessário)
#deploy-redis:
#	kubectl apply -f $(K8S_DIR)/redis-gt.yaml
#
## Aplica os manifests da aplicação com substituição dinâmica da tag
#deploy-app:
#	IMAGE_TAG=$(IMAGE_TAG) envsubst < $(K8S_DIR)/gt.yaml | kubectl apply -f -
#
## Reinicia o pod da aplicação
#restart:
#	kubectl rollout restart deployment gt-dash -n gt-dash

# Executa todo o processo completo
#full-deploy: print-tag build wait-image deploy-redis deploy-app restart
full-deploy: print-tag build wait-image
