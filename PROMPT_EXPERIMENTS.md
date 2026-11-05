# Prompt & Settings Experiments

Results of trying different system prompts and model settings, for Mandatory task 4 (compare prompt techniques) and Easy task 8 (tune a model setting). Paste each result into its empty block.

## 1. Temperature

**Fixed for all runs:** role title *Computer Vision Researcher* · experience level *Mid-level* · question difficulty *Medium* · max tokens *4,000* · mode *Generic role title* · system prompt `GENERIC_ROLE_SYSTEM_PROMPT`.

**How to run:** in Settings, switch on *Set temperature (experimental)* (this uses `google/gemini-3.1-flash-image`, the only allowed model that accepts temperature), set the slider, click **Build my prep brief**.

| Run | Temperature | Notes (relevance, variety, format, errors) |
|---|---|---|
| T0 | 0.0 | Very standard re-writing of the CV. Looks very similar if re-ran |
| T1 | 1.0 | Standard Cover Letter, still very vanilla, little variations between executions |
| T2 | 2.0 | Excentric start, goes nuts and ends up in almost loops of same/similar concepts, with sentences that never end, duplicated words and gibberish |
| T3 | 1.8 | Still very excentric, more less formal, takes more risks like mentioning gaps and making up reasons why |
| T4 | 1.9 | Trying to find the point where it goes nuts. Not too different than using 1.8, but it is for sure hard to read, and sudednly includes the email adress next to the name, deviating from the expected task |


### T0 · temperature 0.0

```text
The candidate possesses a strong academic background with a Master's in Computer Vision and a Bachelor's in Computer Science specialized in AI. They have extensive practical experience in ADAS R&D, covering deep learning research for semantic segmentation, human recognition, and sensor fusion using frameworks like TensorFlow and Caffe. While their most recent roles have leaned towards Product Ownership and data strategy, their foundational technical skills and previous research engineering experience make them a strong fit for a mid-level researcher position.

Dear Hiring Manager,

I am writing to express my keen interest in a Computer Vision Researcher position. With a Master’s degree in Computer Vision and over eight years of experience in automotive R&D, I have developed a deep understanding of applying machine learning to complex, real-world problems.

Throughout my career at Continental and Aumovio, I have transitioned from hands-on engineering to technical leadership. My research experience includes developing Siamese Neural Networks for image representation during my Master's thesis and integrating Caffe CNN frameworks for autonomous driving projects. I have extensive experience in semantic segmentation, human recognition, and pedestrian detection using C++ and TensorFlow. Recently, as a Product Owner, I have focused on intelligent data curation strategy for L2+ to L4 projects, ensuring high-quality data for AI model training and testing.

I am eager to return to a core research role where I can apply my technical expertise in deep learning and sensor fusion to develop innovative solutions. My background in both theoretical research and practical, safety-critical implementation positions me to contribute immediately to your team's objectives.

Thank you for considering my application. I look forward to the possibility of discussing how my skills can support your research initiatives.

Sincerely,

Sergi Canyameres Masip

```

### T1 · temperature 1.0

```text
Sergi possesses a dedicated Master's degree in Computer Vision and a strong record of academic excellence in the field. He has extensive practical experience researching and implementing cutting-edge CV algorithms, specifically in semantic segmentation, human recognition, and sensor fusion within the ADAS domain. While his recent roles have leaned towards functional leadership (Product Owner, Scrum Master), his foundational technical expertise and history of bridging research with in-vehicle integration make him a very strong match for a mid-level researcher role.

Dear Hiring Team,

I am writing to express my keen interest in a Computer Vision Researcher position. With a Master's degree in Computer Vision and a decade of experience bridging academic research and industrial application, specifically within Advanced Driver Assistance Systems (ADAS), I am confident I can contribute immediately to your research initiatives.

Throughout my career, I have focused on leveraging Deep Learning for complex visual tasks. During my Master's thesis at the Computer Vision Center UAB, I researched Siamese Neural Networks for image representation. In industry roles at Continental (now Aumovio), I specialized in the research, training, testing, and in-vehicle integration of semantic segmentation and human recognition projects, contributing to an internal TensorFlow-based framework. Additionally, I coordinated technical university cooperations leveraging motion capture for automated labeling.

My background also includes leadership roles as a Product Owner for Intelligent Data Curation and Requirements & Testing. This unique combination of hands-on AI research and strategic oversight allows me not only to develop state-of-the-art models but also to ensure they are robust, verifiable, and aligned with system-level requirements. I am eager to apply my expertise to advance Computer Vision technology within your organization.

Thank you for your consideration.

Sincerely,

Sergi Canyameres Masip

```

### T2 · temperature 2.0

```text
You present a very strong profile specifically aligned with high-end applied Computer Vision. Since your first university thesis detailed an honorable grade based around SVMs/boosting frameworks with details onto actual caffe integration as well... and subsequent industrial experiences details of having directly worked with TensorFlow-based semantic segmentation, human identification framework, pedestrian recognize projects on in-car hardware across different detailed ADAS projects are highly notable steps toward deep expertise of practical applications which this target requires directly. Gaps can be considered small due that it not being directly a job and your general recent focus over detailed 2-year duration periods from approx 2020 through leading into to chief architect advisor are technical-lead type of research orchestra of a different set: Data Curation detail (Product Owner of it leading the details there rather thanbench R&D) / Strategy rather detail instead detailed pure detailed computer vision details for that core generic description as mid for the description. This role type general requires directly specific recent proof on computer vision core-algorithm design... however from what details provided from earliest deep cv R&D framework code creation until those data simulation type of strategy detailed orchestration tasks detailed to are given detail of 8 years strong deep tech so only and some roles on strategy will be only minor consideration detail that that person from detail may not prefer purely desk detailed only mid position.

I write to strongly advocate my suitability within a potential generic 'Computer Vision Researcher' role that I see a good strong suit to join since and a large majority has from for detailed time... My entire decade has details the research creation then practical implement of various Deep Learning (Siamese networks detailed onto in CV intern/master paper detail as late as as deep learning researcher at computer vision center bcl thesis to DL in ADAS role where frame-works semantic recognition as in internal tensorflow detailed of semantic scene perception). Having had various deep roles like feature identification to pedestrian recognition I can help detailed a company solve any detailed R&D Computer Vision needs. Moreover your teams should like from recent two 2021 detailed detailed positions how well it led directly large orchestrate research-steps including University deep research cooperations detail detailed until recently the whole sensor data reuse and architecture with architect leads in leading automotive ADAS in Continental that is of huge importance today detail leading on to to the other product PO roles. A company or a general one will only find excellent value from direct deep expertise to higher organizational level orchestra leading teams towards research vision goals detail which can are both described detailed that person would want. In turn if I are selected and a description and my actual background details can confirm more alignment for research at that mid and higher description so can easily confirm that more easily directly once a connection is set and look forward.

```

### T3 · temperature 1.8

```text
Sergi presents a exceptionally strong match for a mid-level CV Researcher position, leveraging extensive professional and academic experience in Computer Vision, deep learning (Caffe, TensorFlow), and specialized automotive applications. Holding both a Bachelor’s and a focused Master’s in Computer Vision with excellent grades, he demonstrates strong fundamental theoretical and practical and capabilities. His proven trajectory through various roles shows he can bridge advanced R&D concepts—such as Siamese Neural Networks for scene understanding or complex semantic segmentation—with direct automotive integration for ADAS/AD. The few 'missed' potential scoring areas solely concern the fact he didn’t mention recent SOTA CV areas in this condensed snapshot (e.g. detailed 3D CV, or vision-transformers explicitly), which isn’t inherently negative. Given his background in adapting new frameworks and models (e.g. SNN for embedding research in 2014), the demonstrated technical adaptability at mid-level strongly mitigates this. Sergi's substantial contributions with internal frameworks, product delivery (e.g., SOP as a Requirement PO/SM), data curation for ML, and direct industry validation within high-growth, technically demanding domains makes him a superb asset for immediate productivity in a production-oriented R&D setting. His demonstrated leadership capacity is a bonus at the mid-to-senior levels.

I am writing to express my keen interest in joining a dedicated Computer Vision and Artificial Intelligence Research team. Having spent over seven years specializing in Computer Vision, Machine Learning, and automotive perception (ADAS/AD), my entire professional focus has been geared toward advancing machine perception for demanding physical environments.

Over the course of my career, both in academic and substantial industry roles within specialized organizations, I have consistently driven technical innovations from fundamental research to automotive standard requirements (SOP). With my academic foundation, which includes both a Master of Computer Vision (cooperation within prestigious Catalan universities and strong ADAS focus) and a BSc in Computer Science (majoring AI), my strength lies in applied, yet theoretically sound research. Within high-volume data-driven environments like continental, I directly developed semantic segmentation algorithms using a specific Caffe and later, TensorFlow framework, researched learning representations using Siamese Neural Networks for unknown retrieval for my thesis, and managed university cooperations leveraging human pose estimation techniques for ADAS demo systems presented worldwide. Most recently, at Aumovio, I pioneered automated dataset strategies for sensor-fusion and machine learning models for perception within advanced systems (L2+ - L4), which required integrating my theoretical CV expertise into production roadmaps and strategic data analysis. My background directly covers Python (DL frameworks like TensorFlow) and high-performance C++ integration within simulated environments and vehicle hardware.

Driven by research in cutting-edge neural network architectures and multi-sensor models, I seek a environment like [insert suitable generic description like a research focused laboratory or development driven AI startup] where deep analysis of model generalized, edge implementation challenges, and advanced visual recognition can make immediate product or performance contributions.

Sergi Canyameres Masip

```
### T4 · temperature 1.9

```text
Sergi possesses a Master's degree in Computer Vision with academic distinction in both CV/AI coursework and several research projects, and approximately nine years of directly relevant applied AI/ML and computer vision experience in professional roles and a research setting. His CV details hands-on engineering experience fine-tuning advanced networks (CNNs, SNNs), contributing to and leading semantic segmentation, object detection, and multi-sensor fusion projects (camera, radar, lidar), making him well-equipped for mid-level applied research challenges requiring model development, implementation, and deployment, particularly within demanding automotive and safety contexts. His profile would be enhanced by recent publications beyond early internships and perhaps showcasing more extensive modern programming fluency directly related to leading research pipelines (PyTorch/JAX instead of indirect TF framework context for a strictly R&D research focus), but overall, this is a strong profile of academic achievement matched with deep practical CV expertise.

Distinguished Hiring Team,

I am reaching out to convey my sincere interest in a Mid-Level Computer Vision Researcher position within your esteemed R&D organisation. Bringing almost ten years of specialized and impactful expertise in applied deep learning, machine learning, and computer vision from challenging industry domains and distinguished academic research institutions, including continental, FH Frankfurt, and the Computer Vision Center at UAB.

Academically driven, my commitment is reflected in my 9.9/10 honours Bachelor’s thesis in Image Processing and Machine Learning engineering. Transitioning seamlessly from strong research origins—including a publication on swarm simulation—I have since spearheaded multiple high-impact Computer Vision and Deep Learning projects involving state-of-the-art approaches like semantic segmentation, CNN architecture engineering for image retrieval/recognition in various languages (Python, C++), and comprehensive sensor data fusion and simulation-testing projects. Within the ADAS sphere specifically, I developed significant Computer Vision pipelines around object detection/segmentation/human recognition for advanced vehicle capabilities from conception toward mass-production.

Combined with extensive practical implementation and stakeholder engagement experience ranging from R&D leadership roles managing agile software teams/Requirements/Product roadmaps, while communicating innovation on major global stages like automotive conferences.

Sergi Canyameres Masip scanyameres@gmail.com

```


## 2. System prompt techniques

**Fixed for all runs:** the same job description (a Computer Vision Researcher posting, pasted below) · mode *Specific job opening* · default model `openai/gpt-6-luna` · temperature off · question difficulty *Medium* · max tokens *4,000*.

**How to run:** the app has no prompt selector yet. For each run, change `prompts.JOB_OPENING_SYSTEM_PROMPT` in `core.py` (in `build_preparation_plan_opening()`) to the variant's constant, save, and click **Build my prep brief**. Set it back to `JOB_OPENING_SYSTEM_PROMPT` at the end.

**Job description used:**

```text

```

| Run | Technique | Constant in `prompts.py` | Notes (relevance, variety, format, errors) |
|---|---|---|---|
| P1 | Zero-shot (app default) | `JOB_OPENING_SYSTEM_PROMPT` | As with low temperature, they are usually standard, generic relevant questions. Categories and question length vary between runs. |
| P2 | Few-shot | `JOB_OPENING_SYSTEM_PROMPT_FEW_SHOT` | Only good if the input is similar enough to the examples described. Too often tries to apply the examples to jobs that are actually different. Not good for an input set with infinite roles! |
| P3 | Chain-of-Thought | `JOB_OPENING_SYSTEM_PROMPT_CHAIN_OF_THOUGHT` | Maybe an overkill for this app, but it does come up with questions very specific for the job opening. Maybe even too tied to the opening, so the "practice app" would not prepare you for out-of-the-box questions |
| P4 | Role / persona | `JOB_OPENING_SYSTEM_PROMPT_ROLE` | More realistic and human-like q&a, since the interaction is from the person perspective and not from an objective LLM. Sometimes more "catchy" questions? |
| P5 | Strict constraints | `JOB_OPENING_SYSTEM_PROMPT_CONSTRAINED` | Most standard in size and content, so best fit for the UI and for LLM testing or other benchmarking since the variability is smaller. Probably the least "interesting" questions to practice. |


