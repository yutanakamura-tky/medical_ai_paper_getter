# Medical_AI Paper Getter
Web scraping system for extracting medical-like AI conference papers.

# Available Conferences
### Machine Learning & Artificial Intelligence
IJCAI, NIPS, ICML, ICLR, IJCNN
### Computer Vision
CVPR, ICCV
### Natural Language Processing
ACL, NAACL, EMNLP, CoNLL, COLING, IJCNLP, EACL, LREC, CL, SEMEVAL, TACL, ALTA, HLT, JEP-TALN-RECITAL, MUC, PACLIC, RANLP, ROCLING-IJCLCLP, TINLAP, TIPSTER

# Usage(1): via command-line
### Overview
Run `medical_ai.py` on the shell:
```
python3 medical_ai.py <CONFERENCE> <YEAR>
```

e.g. For `'nips 2018'`, you get 11 medical-like conference papers:
```
python3 medical_ai.py nips 2018
Connecting...
Searching... 11 matches / 1011
===================================
Hybrid Retrieval-Generation Reinforced Agent for Medical Image Report Generation.
http://papers.nips.cc/paper/7426-hybrid-retrieval-generation-reinforced-agent-for-medical-image-report-generation

Representation Learning for Treatment Effect Estimation from Observational Data.
http://papers.nips.cc/paper/7529-representation-learning-for-treatment-effect-estimation-from-observational-data

Lifelong Inverse Reinforcement Learning.
http://papers.nips.cc/paper/7702-lifelong-inverse-reinforcement-learning

MiME: Multilevel Medical Embedding of Electronic Health Records for Predictive Healthcare.
http://papers.nips.cc/paper/7706-mime-multilevel-medical-embedding-of-electronic-health-records-for-predictive-healthcare

Mental Sampling in Multimodal Representations.
http://papers.nips.cc/paper/7817-mental-sampling-in-multimodal-representations

REFUEL: Exploring Sparse Features in Deep Reinforcement Learning for Fast Disease Diagnosis.
http://papers.nips.cc/paper/7962-refuel-exploring-sparse-features-in-deep-reinforcement-learning-for-fast-disease-diagnosis

Forecasting Treatment Responses Over Time Using Recurrent Marginal Structural Networks.
http://papers.nips.cc/paper/7977-forecasting-treatment-responses-over-time-using-recurrent-marginal-structural-networks

Does mitigating ML's impact disparity require treatment disparity?
http://papers.nips.cc/paper/8035-does-mitigating-mls-impact-disparity-require-treatment-disparity

HOUDINI: Lifelong Learning as Program Synthesis.
http://papers.nips.cc/paper/8086-houdini-lifelong-learning-as-program-synthesis

Bayesian multi-domain learning for cancer subtype discovery from next-generation sequencing count data.
http://papers.nips.cc/paper/8125-bayesian-multi-domain-learning-for-cancer-subtype-discovery-from-next-generation-sequencing-count-data

Life-Long Disentangled Representation Learning with Cross-Domain Latent Homologies.
http://papers.nips.cc/paper/8193-life-long-disentangled-representation-learning-with-cross-domain-latent-homologies
===================================
Medical-like AI papers in NIPS 2018: 11 / 1011
===================================
```

### Options

Use `--copy` option to copy result onto clipboard:

```
python3 medical_ai.py
```

Use `--html` option to display result as HTML link <a> tags:

```
python3 medical_ai.py nips 2018 --html
Connecting...
Searching... 11 match / 1011
===================================
<a href="http://papers.nips.cc/paper/7426-hybrid-retrieval-generation-reinforced-agent-for-medical-image-report-generation" target="_blank" alt="Hybrid Retrieval-Generation Reinforced Agent for Medical Image Report Generation.">Hybrid Retrieval-Generation Reinforced Agent for Medical Image Report Generation.</a><br/>
<a href="http://papers.nips.cc/paper/7529-representation-learning-for-treatment-effect-estimation-from-observational-data" target="_blank" alt="Representation Learning for Treatment Effect Estimation from Observational Data.">Representation Learning for Treatment Effect Estimation from Observational Data.</a><br/>
<a href="http://papers.nips.cc/paper/7702-lifelong-inverse-reinforcement-learning" target="_blank" alt="Lifelong Inverse Reinforcement Learning.">Lifelong Inverse Reinforcement Learning.</a><br/>
<a href="http://papers.nips.cc/paper/7706-mime-multilevel-medical-embedding-of-electronic-health-records-for-predictive-healthcare" target="_blank" alt="MiME: Multilevel Medical Embedding of Electronic Health Records for Predictive Healthcare.">MiME: Multilevel Medical Embedding of Electronic Health Records for Predictive Healthcare.</a><br/>
<a href="http://papers.nips.cc/paper/7817-mental-sampling-in-multimodal-representations" target="_blank" alt="Mental Sampling in Multimodal Representations.">Mental Sampling in Multimodal Representations.</a><br/>
<a href="http://papers.nips.cc/paper/7962-refuel-exploring-sparse-features-in-deep-reinforcement-learning-for-fast-disease-diagnosis" target="_blank" alt="REFUEL: Exploring Sparse Features in Deep Reinforcement Learning for Fast Disease Diagnosis.">REFUEL: Exploring Sparse Features in Deep Reinforcement Learning for Fast Disease Diagnosis.</a><br/>
<a href="http://papers.nips.cc/paper/7977-forecasting-treatment-responses-over-time-using-recurrent-marginal-structural-networks" target="_blank" alt="Forecasting Treatment Responses Over Time Using Recurrent Marginal Structural Networks.">Forecasting Treatment Responses Over Time Using Recurrent Marginal Structural Networks.</a><br/>
<a href="http://papers.nips.cc/paper/8035-does-mitigating-mls-impact-disparity-require-treatment-disparity" target="_blank" alt="Does mitigating ML's impact disparity require treatment disparity?">Does mitigating ML's impact disparity require treatment disparity?</a><br/>
<a href="http://papers.nips.cc/paper/8086-houdini-lifelong-learning-as-program-synthesis" target="_blank" alt="HOUDINI: Lifelong Learning as Program Synthesis.">HOUDINI: Lifelong Learning as Program Synthesis.</a><br/>
<a href="http://papers.nips.cc/paper/8125-bayesian-multi-domain-learning-for-cancer-subtype-discovery-from-next-generation-sequencing-count-data" target="_blank" alt="Bayesian multi-domain learning for cancer subtype discovery from next-generation sequencing count data.">Bayesian multi-domain learning for cancer subtype discovery from next-generation sequencing count data.</a><br/>
<a href="http://papers.nips.cc/paper/8193-life-long-disentangled-representation-learning-with-cross-domain-latent-homologies" target="_blank" alt="Life-Long Disentangled Representation Learning with Cross-Domain Latent Homologies.">Life-Long Disentangled Representation Learning with Cross-Domain Latent Homologies.</a>
===================================
Medical-like AI papers in NIPS 2018: 11 / 1011
===================================
```

Use `--markdown` option to display result as markdown links:

```
python3 medical_ai.py nips 2018 --markdown
Connecting...
Searching... 11 match / 1011
===================================
[Hybrid Retrieval-Generation Reinforced Agent for Medical Image Report Generation.](http://papers.nips.cc/paper/7426-hybrid-retrieval-generation-reinforced-agent-for-medical-image-report-generation)
[Representation Learning for Treatment Effect Estimation from Observational Data.](http://papers.nips.cc/paper/7529-representation-learning-for-treatment-effect-estimation-from-observational-data)
[Lifelong Inverse Reinforcement Learning.](http://papers.nips.cc/paper/7702-lifelong-inverse-reinforcement-learning)
[MiME: Multilevel Medical Embedding of Electronic Health Records for Predictive Healthcare.](http://papers.nips.cc/paper/7706-mime-multilevel-medical-embedding-of-electronic-health-records-for-predictive-healthcare)
[Mental Sampling in Multimodal Representations.](http://papers.nips.cc/paper/7817-mental-sampling-in-multimodal-representations)
[REFUEL: Exploring Sparse Features in Deep Reinforcement Learning for Fast Disease Diagnosis.](http://papers.nips.cc/paper/7962-refuel-exploring-sparse-features-in-deep-reinforcement-learning-for-fast-disease-diagnosis)
[Forecasting Treatment Responses Over Time Using Recurrent Marginal Structural Networks.](http://papers.nips.cc/paper/7977-forecasting-treatment-responses-over-time-using-recurrent-marginal-structural-networks)
[Does mitigating ML's impact disparity require treatment disparity?](http://papers.nips.cc/paper/8035-does-mitigating-mls-impact-disparity-require-treatment-disparity)
[HOUDINI: Lifelong Learning as Program Synthesis.](http://papers.nips.cc/paper/8086-houdini-lifelong-learning-as-program-synthesis)
[Bayesian multi-domain learning for cancer subtype discovery from next-generation sequencing count data.](http://papers.nips.cc/paper/8125-bayesian-multi-domain-learning-for-cancer-subtype-discovery-from-next-generation-sequencing-count-data)
[Life-Long Disentangled Representation Learning with Cross-Domain Latent Homologies.](http://papers.nips.cc/paper/8193-life-long-disentangled-representation-learning-with-cross-domain-latent-homologies)
===================================
Medical-like AI papers in NIPS 2018: 11 / 1011
===================================
```


To browse all available options, input `python3 medical_ai.py -h` or `python3 medical_ai.py --help`:


```
usage: medical_ai.py [-h] [-q] [--copy] [-m | --html]
                     [--title-only | --url-only]
                     conference year

++++++++++++++++++++++++++++++++++++++++++++++++++
Pickup medical AI paper titles and URLs from specified conference and year.
会議名と年数を指定すると, 医療に関連するAI論文のみを探し出してタイトルとURLを列挙します.

To get from ACL 2019, input like this: python3 medical_ai.py acl 2019
例えばACL 2019採択論文から探すには本プログラムを python3 medical medical_ai.py acl 2019 と実行してください.

Conference name is case insensitive.
会議名は大文字でも小文字でも構いません.

To output HTML link tags or markdown links, use options below.
以下に示すオプションを使うと, 結果をHTMLリンクタグやMarkdownリンクとして出力することも可能です.
++++++++++++++++++++++++++++++++++++++++++++++++++

positional arguments:
  conference            specify one conference (e.g. acl)
  year                  specify one year (e.g. 2019)

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           be more quiet
  --copy                copy result to clipboard
  -m, --md, --markdown  output as markdown links
                        collaborates with --url-only
                        ignores --title-only
  --html                output as HTML <a> tags
                        collaborates with --url-only
                        ignores --title-only
  --title-only          output paper title only
  --url-only            output paper URL only
```
