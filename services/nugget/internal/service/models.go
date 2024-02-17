package service

type JobTemplateDefinition struct {
	Job struct {
		Steps []struct {
			Name      string     `json:"name"`
			Artifacts []Artifact `json:"artifacts"`
		} `json:"steps"`
	} `json:"job"`
}

type Artifact struct {
	SourceProject string `json:"source_project"`
	Source        string `json:"source"`
	Destination   string `json:"destination"`
}

type ArchiveFile struct {
	Source          string
	Destination     string
	ExternalProject string
}
