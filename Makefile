all: start

start: _build _run
_build:
	@docker build -f Dockerfile -t rest_backend .
_run:
	@docker run --name rest_backend --network minikube -p 8080:80 rest_backend
	@echo "Point your browser to: http://127.0.0.1:8080/"
stop:
	@docker kill rest_backend || true
	@docker rm rest_backend || true
reload: stop start
