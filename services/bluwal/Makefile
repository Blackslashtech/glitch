.PHONY: lint-go
lint-go:
	golangci-lint run -v --config .golangci.yml

.PHONY: lint-proto
lint-proto:
	cd proto && buf lint

.PHONY: lint
lint: lint-go lint-proto

.PHONY: goimports
goimports:
	gofancyimports fix --local github.com/c4t-but-s4d/neo -w $(shell find . -type f -name '*.go' -not -path "./proto/*")

.PHONY: test
test:
	go test -race -timeout 1m ./...

.PHONY: validate
validate: lint test

.PHONY: proto
proto:
	cd proto && buf generate
	fastmod --accept-all 'from bluwal import' 'from proto.bluwal import' --dir proto/python --iglob '*.py'

.PHONY: repo-proto-not-for-participants
repo-proto-not-for-participants: proto
	rm -rf ../../checkers/bluwal/proto
	cp -r proto/python ../../checkers/bluwal/proto

	@echo "Yeah, we even have sploit(s) for this service!"
	rm -rf ../../sploits/bluwal/proto
	cp -r proto/python ../../sploits/bluwal/proto
