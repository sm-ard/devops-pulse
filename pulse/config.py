# Severity threshold for CVEs (uppercase NVD baseSeverity values).
SEVERITY_MIN = {"HIGH", "CRITICAL"}

# Lowercase keywords; a CVE is kept if any appears in its description.
CVE_KEYWORDS = [
    "kubernetes", "docker", "containerd", "terraform", "helm",
    "istio", "argo", "prometheus", "aws", "gcp", "azure",
    "cilium", "vault", "etcd",
]

# (display name, "owner/repo") for GitHub Releases lookups.
RELEASE_TOOLS = [
    ("Kubernetes", "kubernetes/kubernetes"),
    ("Argo CD", "argoproj/argo-cd"),
    ("Istio", "istio/istio"),
    ("Prometheus", "prometheus/prometheus"),
    ("Helm", "helm/helm"),
    ("Terraform", "hashicorp/terraform"),
    ("Cilium", "cilium/cilium"),
    ("containerd", "containerd/containerd"),
    ("etcd", "etcd-io/etcd"),
    ("Vault", "hashicorp/vault"),
]

# (source label, RSS url)
NEWS_FEEDS = [
    ("Kubernetes Blog", "https://kubernetes.io/feed.xml"),
    ("AWS What's New", "https://aws.amazon.com/about-aws/whats-new/recent/feed/"),
    ("Google Cloud Blog", "https://cloudblog.withgoogle.com/rss/"),
]

NEWS_PER_FEED = 3   # max items taken from each feed
NEWS_MAX = 8        # overall cap across feeds
