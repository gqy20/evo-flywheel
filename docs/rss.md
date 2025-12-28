# 进化生物学期刊RSS源总表

> 更新时间：2025-01-28

---

## 一、核心期刊RSS源总表

| 类别 | 期刊名称 | 出版商 | RSS URL | 状态 | 优先级 |
|------|----------|--------|---------|------|--------|
| **预印本** | arXiv - Populations & Evolution | arXiv | `https://export.arxiv.org/rss/q-bio.PE` | ✅ | P0 |
| **预印本** | arXiv - Quantitative Biology | arXiv | `https://export.arxiv.org/rss/q-bio` | ✅ | P0 |
| **预印本** | bioRxiv (API) | bioRxiv | `https://api.biorxiv.org/details/biorxiv/{start}/{end}?category=evolutionary_biology` | ✅ | P0 |
| **核心** | Evolution | Oxford Academic | `https://academic.oup.com/evolut/rss` | ✅ | P0 |
| **核心** | Molecular Ecology | Wiley | `https://onlinelibrary.wiley.com/rss/journal/1365294X` | ✅ | P0 |
| **核心** | Molecular Ecology Resources | Wiley | `https://onlinelibrary.wiley.com/feed/17550998/most-recent` | ✅ | P1 |
| **核心** | Evolutionary Applications | Wiley | `https://onlinelibrary.wiley.com/rss/journal/17524571` | ✅ | P1 |
| **核心** | Journal of Evolutionary Biology | Wiley | `https://onlinelibrary.wiley.com/rss/journal/14209101` | ✅ | P1 |
| **方法** | **PLOS Computational Biology** | PLOS | `https://journals.plos.org/ploscompbiol/feed/atom` | ✅ | P0 |
| **方法** | **Methods in Ecology & Evolution** | BES/Wiley | `https://besjournals.onlinelibrary.wiley.com/rss/journal/2041210X` | ✅ | P0 |
| **方法** | **Bioinformatics** | Oxford Academic | 需在页面获取 | ⚠️ | P0 |
| **方法** | Briefings in Bioinformatics | Oxford Academic | 需在页面获取 | ⚠️ | P1 |
| **方法** | BMC Bioinformatics | BMC | `https://bmcbioinformatics.biomedcentral.com/rss` | ✅ | P1 |
| **方法** | Molecular Biology and Evolution | Oxford Academic | 需在页面获取 | ⚠️ | P0 |
| **方法** | Systematic Biology | Oxford Academic | 需在页面获取 | ⚠️ | P0 |
| **方法** | Molecular Phylogenetics and Evolution | Elsevier | ScienceDirect平台 | ⚠️ | P1 |
| **生态** | Ecology Letters | Wiley | `https://onlinelibrary.wiley.com/rss/journal/1461023x` | ✅ | P1 |
| **生态** | The American Naturalist | Chicago Press | `https://www.journals.uchicago.edu/toc/an/current` | ✅ | P1 |
| **生态** | Evolutionary Ecology | Springer | `https://link.springer.com/journal/10682/rss` | ✅ | P2 |
| **生态** | Proceedings of the Royal Society B | Royal Society | `https://royalsocietypublishing.org/rss/procb` | ✅ | P1 |
| **生态** | Nature Ecology & Evolution | Nature | `https://www.nature.com/natecolevol/rss` | ✅ | P0 |
| **综合** | **Nature** | Nature | `https://www.nature.com/nature.rss` | ✅ | P0 |
| **综合** | **Science** | AAAS | 需查看官方页面 | ⚠️ | P0 |
| **综合** | Current Biology | Cell Press | `https://www.cell.com/current-biology/rss` | ❌ Cloudflare | P1 |
| **综合** | eLife | eLife | `https://elifesciences.org/rss.xml` | ✅ | P1 |
| **综合** | **PLOS Biology** | PLOS | `https://journals.plos.org/plosbiology/feed/atom` | ✅ | P0 |
| **综合** | **PLOS Genetics** | PLOS | `https://journals.plos.org/plosgenetics/feed/atom` | ✅ | P0 |
| **综合** | Nature Communications | Nature | `https://www.nature.com/ncomms/rss` | ✅ | P1 |
| **综合** | Nature Genetics | Nature | `https://feeds.nature.com/ng/rss/current` | ✅ | P1 |
| **综合** | Nature Methods | Nature | `https://feeds.nature.com/nmeth/rss/current` | ✅ | P1 |
| **综合** | Genome Biology | BMC | `https://genomebiology.biomedcentral.com/rss` | ✅ | P1 |
| **综合** | Genome Research | CSHL | `https://genome.cshlp.org/rss/current.xml` | ✅ | P2 |
| **综合** | Nucleic Acids Research | Oxford Academic | 需在页面获取 | ⚠️ | P1 |
| **综合** | G3: Genes|Genomes|Genetics | Oxford Academic | 需在页面获取 | ⚠️ | P2 |

---

## 二、RSS URL格式说明

### 1. Wiley期刊（标准格式）
```
https://onlinelibrary.wiley.com/rss/journal/{ISSN}
```

示例：
- Molecular Ecology: `1365294X`
- Methods Ecol Evol: `2041210X`

### 2. PLOS期刊（开放获取）
```
https://journals.plos.org/{journal}/feed/atom
```

期刊代码：
- `ploscompbiol` - Computational Biology
- `plosbiology` - Biology
- `plosgenetics` - Genetics

### 3. Nature期刊
```
https://www.nature.com/{journal}/rss
```

期刊代码：
- `nature` - Nature主刊
- `natecolevol` - Ecology & Evolution
- `ncomms` - Communications

### 4. Oxford Academic期刊
需要手动在期刊页面获取：
1. 访问期刊页面
2. 找到"RSS"或"Alerts"
3. 选择类型（Latest Issue、Advance Articles等）

### 5. bioRxiv API（推荐）
```
https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}?category={category}
```

参数：
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `category`: evolutionary_biology, genomics等

---

## 三、按研究兴趣分类

### 🔬 群体遗传学/群体基因组学
| 期刊 | 优先级 | RSS |
|------|--------|-----|
| Molecular Ecology | ⭐⭐⭐⭐⭐ | ✅ |
| Evolutionary Applications | ⭐⭐⭐⭐ | ✅ |
| Journal of Evolutionary Biology | ⭐⭐⭐ | ✅ |
| Molecular Ecology Resources | ⭐⭐⭐⭐ | ✅ |
| G3: Genes|Genomes|Genetics | ⭐⭐⭐ | ⚠️ |
| PLOS Genetics | ⭐⭐⭐⭐⭐ | ✅ |

### 💻 计算方法/生物信息学
| 期刊 | 优先级 | RSS |
|------|--------|-----|
| **PLOS Computational Biology** | ⭐⭐⭐⭐⭐ | ✅ |
| **Methods in Ecology & Evolution** | ⭐⭐⭐⭐⭐ | ✅ |
| **Bioinformatics** | ⭐⭐⭐⭐⭐ | ⚠️ |
| Briefings in Bioinformatics | ⭐⭐⭐⭐ | ⚠️ |
| BMC Bioinformatics | ⭐⭐⭐ | ✅ |

### 🧬 分子进化
| 期刊 | 优先级 | RSS |
|------|--------|-----|
| **Molecular Biology and Evolution** | ⭐⭐⭐⭐⭐ | ⚠️ |
| Genome Biology | ⭐⭐⭐⭐ | ✅ |
| PLOS Genetics | ⭐⭐⭐⭐ | ✅ |
| Nature Genetics | ⭐⭐⭐⭐ | ✅ |
| Genome Research | ⭐⭐⭐ | ✅ |

### 🌳 系统发育学
| 期刊 | 优先级 | RSS |
|------|--------|-----|
| **Systematic Biology** | ⭐⭐⭐⭐⭐ | ⚠️ |
| Molecular Phylogenetics and Evolution | ⭐⭐⭐⭐ | ⚠️ |
| Cladistics | ⭐⭐⭐ | ✅ |

### 🌿 生态进化
| 期刊 | 优先级 | RSS |
|------|--------|-----|
| Ecology Letters | ⭐⭐⭐⭐ | ✅ |
| Evolutionary Ecology | ⭐⭐⭐ | ✅ |
| The American Naturalist | ⭐⭐⭐⭐ | ✅ |
| Proceedings B | ⭐⭐⭐⭐ | ✅ |
| Nature Ecology & Evolution | ⭐⭐⭐⭐⭐ | ✅ |

---

## 四、快速配置（推荐源）

### MVP配置（7个核心源）
```yaml
必选:
  - arXiv q-bio.PE
  - bioRxiv API
  - PLOS Computational Biology
  - Methods in Ecology & Evolution
  - Molecular Ecology
  - Nature
  - PLOS Biology
```

### 完整配置（20个源）
```yaml
预印本 (3):
  - arXiv q-bio.PE
  - bioRxiv API
  - arXiv q-bio

核心期刊 (5):
  - Evolution
  - Molecular Ecology
  - Molecular Ecology Resources
  - Nature Ecology & Evolution
  - eLife

方法工具 (6):
  - PLOS Computational Biology
  - Methods in Ecology & Evolution
  - Bioinformatics
  - BMC Bioinformatics
  - PLOS Biology
  - PLOS Genetics

综合期刊 (6):
  - Nature
  - Science
  - Nature Communications
  - Nature Genetics
  - Genome Biology
  - Proceedings B
```

---

## 五、状态说明

| 状态 | 说明 | 可用性 |
|------|------|--------|
| ✅ | 已验证可用 | 直接使用 |
| ⚠️ | 需手动获取 | 访问页面获取RSS |
| ❌ | Cloudflare保护 | 使用API或RSSHub |

### Cloudflare保护解决方案

**Current Biology** 等期刊：
```python
# 方案1: 使用bioRxiv API（推荐）
url = f"https://api.biorxiv.org/details/biorxiv/{start}/{end}?category=evolutionary_biology"

# 方案2: 自部署RSSHub
url = "https://your-rsshub.com/cell/current-biology"

# 方案3: 等待正式发表后在PubMed查找
```

---

## 六、Python使用示例

```python
import feedparser
import requests

# 配置源
SOURCES = {
    # 预印本
    "arxiv_pe": "https://export.arxiv.org/rss/q-bio.PE",

    # 方法工具（用户关注）
    "plos_compbio": "https://journals.plos.org/ploscompbiol/feed/atom",
    "methods_eecol": "https://besjournals.onlinelibrary.wiley.com/rss/journal/2041210X",
    "mol_ecol_res": "https://onlinelibrary.wiley.com/feed/17550998/most-recent",

    # 核心期刊
    "evolution": "https://academic.oup.com/evolut/rss",
    "mol_ecology": "https://onlinelibrary.wiley.com/rss/journal/1365294X",

    # Nature
    "nature": "https://www.nature.com/nature.rss",
    "nature_eco_evol": "https://www.nature.com/natecolevol/rss",

    # PLOS
    "plos_biology": "https://journals.plos.org/plosbiology/feed/atom",
    "plos_genetics": "https://journals.plos.org/plosgenetics/feed/atom",
}

def fetch_papers():
    all_papers = []

    for name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            print(f"{name}: {len(feed.entries)} 篇")

            for entry in feed.entries[:20]:  # 每个源最多20篇
                all_papers.append({
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "summary": entry.get("description", "")[:200],
                    "date": entry.get("published"),
                    "source": name
                })
        except Exception as e:
            print(f"{name} 失败: {e}")

    return all_papers

# 使用
papers = fetch_papers()
print(f"\n总计: {len(papers)} 篇论文")
```

### bioRxiv API使用
```python
def fetch_biorxiv(days=7):
    from datetime import datetime, timedelta

    end = datetime.now()
    start = end - timedelta(days=days)

    url = f"https://api.biorxiv.org/details/biorxiv/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
    params = {"category": "evolutionary_biology", "format": "json"}

    response = requests.get(url, params=params)
    data = response.json()

    papers = data.get("collection", [])
    print(f"bioRxiv: {len(papers)} 篇")

    return papers
```

---

## 七、期刊网址快速索引

### 期刊名称 → 网址速查

| 期刊 | 网址关键词 | 快速访问 |
|------|-----------|----------|
| PLOS Computational Biology | ploscompbiol | journals.plos.org/ploscompbiol |
| Methods Ecol Evol | methods-ecol-evol | besjournals.onlinelibrary.wiley.com |
| Molecular Ecology | molecular-ecology | onlinelibrary.wiley.com/journal/1365294x |
| Bioinformatics | bioinformatics | academic.oup.com/bioinformatics |
| Evolution | evolution | academic.oup.com/evolut |
| Nature Ecology & Evolution | natecolevol | nature.com/natecolevol |
| MBE | mbe | academic.oup.com/mbe |
| Systematic Biology | sysbio | academic.oup.com/sysbio |

---

## 八、常见问题

**Q: Bioinformatics的RSS在哪里？**
A: 访问 https://academic.oup.com/bioinformatics → 点击"RSS"或"Alerts"

**Q: Current Biology为什么不能用？**
A: Cell Press使用Cloudflare保护，建议使用bioRxiv API获取预印本

**Q: Oxford期刊的RSS格式？**
A: 不统一，需要到期刊页面手动获取

**Q: PLOS有几种RSS？**
A: 两种：`/feed/atom` (推荐) 和 `/feed/rss`

**Q: 如何获取最新数据？**
A: 建议每天运行一次采集任务

---

## 九、更新日志

| 日期 | 内容 |
|------|------|
| 2025-01-28 | 初始版本，30+期刊 |
| 2025-01-28 | 添加方法工具类期刊 |
| 2025-01-28 | 测试验证PLOS、arXiv |
| 2025-01-28 | 整合所有文档到总表 |
