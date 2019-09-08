# Medical_AI Paper Getter
Web scraping system for extracting medical-like AI conference papers.

# Available Conferences
### Machine Learning & Artificial Intelligence
IJCAI, NIPS, ICML, ICLR, IJCNN
### Computer Vision
CVPR, ICCV
### Natural Language Processing
ACL, NAACL, EMNLP, CoNLL, COLING, IJCNLP, EACL, LREC, CL, SEMEVAL, TACL, ALTA, HLT, JEP-TALN-RECITAL, MUC, PACLIC, RANLP, ROCLING-IJCLCLP, TINLAP, TIPSTER


# Usage(1): In Python3 Code

### Overview

Import module:

```Python3
import medical.ai
```

To get medical-like AI papers in CVPR 2017 & 2018, create a Query instance and use .search() method:

```Python3
query = medical.ai.Query(conference='cvpr', year=[2017, 2018])
result = query.search()
```

```
>>> Connecting for CVPR 2017 ...
>>> Connecting for CVPR 2018 ...
>>> Download from CVPR 2017 ... 784 papers Complete!
>>> Download from CVPR 2018 ... 980 papers Complete!
```

Get information of medical-like AI papers:

```Python3
for conference in result:
    print(conference.conference_name)
    print(conference.year)
    for paper in conference.medical_ai_papers:
        print(paper.title)
        print(paper.url)
        print(paper.author)     # list ['author1', 'author2', ... ]
        print(paper.abstract)
```

Get information of medical-like & non-medical-like AI papers:

```Python3
for conference in result:
    print(conference.conference_name)
    print(conference.year)
    for paper in conference.papers:
        print(paper.title)
        print(paper.url)
        print(paper.author)     # list ['author1', 'author2', ... ]
        print(paper.abstract)
        print(paper.medical)  # True or False
```



### Quiet Mode

If you want standard output to be more quiet, use config as this:
```Python3
import medical.ai
myconfig = medical.ai.Config(quiet=True)
query = medical.ai.Query(conference='cvpr', year=[2017, 2018])
result = query.search(config=myconfig)
```






# Usage(2): via command-line
### Overview
Run `medical/ai.py` on the shell:
```
python3 medical/ai.py <CONFERENCE> <YEAR>
```

e.g. For `'cvpr 2017'`, you get 8 medical-like conference papers:
```
python3 medical/ai.py cvpr 2017
Connecting for CVPR 2017 ...
Downloading from CVPR 2017 ... 784 papers Complete!
===================================

CVPR 2017

Direct Photometric Alignment by Mesh Deformation.
https://doi.org/10.1109/CVPR.2017.289

ChestX-Ray8: Hospital-Scale Chest X-Ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases.
https://doi.org/10.1109/CVPR.2017.369

MDNet: A Semantically and Visually Interpretable Medical Image Diagnosis Network.
https://doi.org/10.1109/CVPR.2017.378

Joint Sequence Learning and Cross-Modality Convolution for 3D Biomedical Segmentation.
https://doi.org/10.1109/CVPR.2017.398

Fine-Tuning Convolutional Neural Networks for Biomedical Image Analysis: Actively and Incrementally.
https://doi.org/10.1109/CVPR.2017.506

Simultaneous Super-Resolution and Cross-Modality Synthesis of 3D Medical Images Using Weakly-Supervised Joint Convolutional Sparse Coding.
https://doi.org/10.1109/CVPR.2017.613

Multiple-Scattering Microphysics Tomography.
https://doi.org/10.1109/CVPR.2017.614

Expert Gate: Lifelong Learning with a Network of Experts.
https://doi.org/10.1109/CVPR.2017.753


===================================
Medical-like AI papers in CVPR 2017: 8 / 784

```

Use `-m` or `-markdown` option to display result as markdown links:

```
python3 medical/ai.py cvpr 2017 -m
Connecting for CVPR 2017 ...
Downloading from CVPR 2017 ... 784 papers Complete!
===================================

CVPR 2017

[Direct Photometric Alignment by Mesh Deformation.](https://doi.org/10.1109/CVPR.2017.289)

[ChestX-Ray8: Hospital-Scale Chest X-Ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases.](https://doi.org/10.1109/CVPR.2017.369)

    ...

[Expert Gate: Lifelong Learning with a Network of Experts.](https://doi.org/10.1109/CVPR.2017.753)

===================================
Medical-like AI papers in CVPR 2017: 8 / 784
```

Use `--copy` option to copy result onto clipboard:

```
python3 medical/ai.py cvpr 2017 -m --copy
Connecting for CVPR 2017 ...
Downloading from CVPR 2017 ... 784 papers Complete!
===================================

CVPR 2017

[Direct Photometric Alignment by Mesh Deformation.](https://doi.org/10.1109/CVPR.2017.289)

[ChestX-Ray8: Hospital-Scale Chest X-Ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases.](https://doi.org/10.1109/CVPR.2017.369)

[MDNet: A Semantically and Visually Interpretable Medical Image Diagnosis Network.](https://doi.org/10.1109/CVPR.2017.378)

        ...

[Expert Gate: Lifelong Learning with a Network of Experts.](https://doi.org/10.1109/CVPR.2017.753)

===================================
Medical-like AI papers in CVPR 2017: 8 / 784
 * * * Copied this result to clipboard * * *
```


To browse all available options, input `python3 medical/ai.py -h` or `python3 medical/ai.py --help`:


```
usage: medical/ai.py [-h] [-q] [--copy] [-m | --html]
                     [--title-only | --url-only]
                     conference year

++++++++++++++++++++++++++++++++++++++++++++++++++
Pickup medical AI paper titles and URLs from specified conference and year.
会議名と年数を指定すると, 医療に関連するAI論文のみを探し出してタイトルとURLを列挙します.

To get from ACL 2019, input like this: python3 medical/ai.py acl 2019
例えばACL 2019採択論文から探すには本プログラムを python3 medical medical/ai.py acl 2019 と実行してください.

Conference name is case insensitive.
会議名は大文字でも小文字でも構いません.

To output HTML link tags or markdown links, use options below.
以下に示すオプションを使うと, 結果をHTMLリンクタグやMarkdownリンクとして出力することも可能です.
++++++++++++++++++++++++++++++++++++++++++++++++++

positional arguments:
  conferences_and_years
                        speficy conferences and years
                         example1: acl 2019
                         example2: acl naacl 2019
                         example3: acl 2018 2019
                         example4: acl naacl 2018 2019

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           be more quiet
  --copy                copy result to clipboard
  -a, --all             get also non-medical AI papers
  -m, --md, --markdown  output as markdown links
                        collaborates with --url-only
                        ignores --title-only
  --html                output as HTML <a> tags
                        collaborates with --url-only
                        ignores --title-only
  --title-only          output paper title only
  --url-only            output paper URL only
```
