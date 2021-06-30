.PHONY: setup-multiarch
setup-multiarch:
	docker buildx create --name multiarch --use

.PHONY: build-and-push-multiarch
build-and-push-multiarch:
	docker buildx use multiarch
	docker buildx build \
		--platform linux/arm64/v8 \
		-t ghcr.io/threadproc/hotdog-or-not:latest \
		--push .