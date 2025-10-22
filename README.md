# MedAgentSim: Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions
<div align="center">
  <img src="assets/Tom_Moreno_scaled_10x_pngcrushed.jpg" alt="MedAgentSim Logo" width="100"/>
  <p><i>An open-source framework for simulating realistic doctor-patient interactions</i></p>
</div>
<a href="https://arxiv.org/abs/2503.22678">
  <img src="https://img.shields.io/badge/📝-Paper-blue" height="25">
</a>
<a href="https://www.youtube.com/watch?v=0qmC0ovWcr4">
  <img src="https://img.shields.io/badge/🎥-Video-red" height="25">
</a>
<a href="https://github.com/MAXNORM8650/MedAgentSim/graphs/contributors">
  <img src="https://img.shields.io/github/contributors/MAXNORM8650/MedAgentSim" height="25">
</a>
<a href="https://github.com/MAXNORM8650/MedAgentSim/stargazers">
  <img src="https://img.shields.io/github/stars/MAXNORM8650/MedAgentSim" height="25">
</a>
<a href="https://github.com/MAXNORM8650/MedAgentSim/network/members">
  <img src="https://img.shields.io/github/forks/MAXNORM8650/MedAgentSim" height="25">
</a>
<a href="https://github.com/MAXNORM8650/MedAgentSim/issues">
  <img src="https://img.shields.io/github/issues/MAXNORM8650/MedAgentSim" height="25">
</a>
<a href="https://github.com/MAXNORM8650/MedAgentSim/blob/main/LICENSE">
  <img src="https://img.shields.io/github/license/MAXNORM8650/MedAgentSim" height="25">
</a>
<a href="https://medagentsim.netlify.app/">
  <img src="https://img.shields.io/badge/🌐-Website-green" height="25">
</a>
<a href="https://www.python.org/downloads/">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" height="25">
</a>
<a href="https://huggingface.co/ItsMaxNorm/MedAgentSim-datasets">
  <img src="https://img.shields.io/badge/HuggingFace-Datasets-orange" height="25">
</a>

## 📣 Recent Updates

* [13/05/2025] 🎉 Our paper **MedAgentSim: Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions** has been accepted early at **MICCAI 2025**.
* [31/03/2025] 🔥 We release **MedAgentSim: Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions**.


## 🔍 Overview

MedAgentSim is an open-source simulated hospital environment designed to evaluate and enhance large language model (LLM) performance in dynamic diagnostic settings. Unlike prior approaches, our framework requires doctor agents to actively engage with patients through multi-turn conversations, requesting relevant medical examinations and imaging results to mimic real-world diagnostic processes.

Key features:
- **Multi-Agent Architecture**: Doctor, patient, and measurement agents interact in a realistic clinical setting
- **Self-Improvement Mechanisms**: Models iteratively refine their diagnostic strategies through experience
- **Experience Replay**: Past successful diagnoses inform future cases through knowledge retrieval
- **Visual Game Simulation**: Built with Phaser for an intuitive, interactive environment
- **Multi-Modal Capabilities**: Integration with vision language models for medical image interpretation


## 🚀 Quick Start

### Prerequisites

```bash
# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Clone the repository
git clone https://github.com/MAXNORM8650/MedAgentSim.git
cd MedAgentSim
pip install e .
# Install dependencies
pip install -r requirements.txt
# Ensure
pip install --upgrade torch torchao torchvision transformers
pip install --upgrade openai
python -m pip install replicate
python -m pip install  anthropic
python -m pip install groq
python -m pip install accelerate
```

### Running the Simulation

```bash
# Start the server
python -m medsim.server

# In a separate terminal, launch the client
python -m medsim.simulate
```
Visit `http://localhost:8000/simulator` in your browser.

### Interactive Web Demo

You can explore a lightweight, self-contained demo of a MedAgentSim patient in your browser. The web
app streams responses from the structured MedQA dataset so it runs without accessing external LLMs.

```bash
uvicorn medsim.webapp.app:app --reload
```

Then open `http://127.0.0.1:8000/` to start a session. Ask questions, request physical exam findings,
and reveal the reference diagnosis when you are ready.

### Host models using vLLM to query
```bash
vllm serve unsloth/Llama-3.2-11B-Vision-Instruct-unsloth-bnb-4bit --dtype 'auto'  --quantization "bitsandbytes" --load_format "bitsandbytes" --tensor-parallel-size 4 --max-model-len 8192 --limit-mm-per-prompt image=1

vllm serve llava-hf/llava-v1.6-mistral-7b-hf --tensor-parallel-size 4
vllm serve unsloth/Llama-3.3-70B-Instruct-bnb-4bit --quantization "bitsandbytes" --load_format "bitsandbytes"
```
## 🏥 Simulation Modes

MedAgentSim supports three core interaction modes:

1. **Generation Mode**: Patient agent autonomously creates cases, generating illnesses, symptoms, and test results
2. **Dataset Mode**: Patient responses derived from predefined medical datasets
3. **Control Mode**: Human users can control either the doctor or patient agent for real-time interaction

## 🧠 Model Support

MedAgentSim is compatible with various LLMs:

- **Open-Source Models**: LLaMA 3.3, Mistral, Mixtral, Qwen2
- **Vision-Language Models**: LLaVA 1.5, QwenVL
- **Custom Models**: Integrate your own models following our documentation

## 📊 Benchmarks

MedAgentSim has been evaluated on several medical benchmarks:

| Benchmark | Description | #Cases |
|-----------|-------------|--------|
| NEJM | Complex real-world cases | 15 |
| NEJM Extended | Additional complex cases | 120 |
| MedQA | Simulated diagnostic scenarios | 106 |
| MedQA Extended | Extended diagnostic scenarios | 214 |
| MIMIC-IV | Real-world clinical cases | 288 |

1.	Launch the vLLM server (with appropriate GPUs):
```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 8192
```
2.	Run the simulation:
```bash
python medsim/main.py \
    --doctor_llm meta-llama/Llama-3.1-70B-Instruct \
    --patient_llm meta-llama/Llama-3.1-70B-Instruct \
    --measurement_llm meta-llama/Llama-3.1-70B-Instruct \
    --moderator_llm meta-llama/Llama-3.1-70B-Instruct \
    --agent_dataset MedQA
```
## 🧩 Project Structure

```
MedAgentSim/
├── assets/               # Images, CSS, and other static files
├── datasets/             # Sample datasets and medical knowledge base. Put your dataset here
├── docs/                 # Documentation. Coming soon
├── medsim/               # Core simulation code
│   ├── configs/          # configs for for models
│   ├── core/             # Agent implementations
│   ├── server/           # Simulation environment server
│   ├── simulate/         # Multi-agnet running interfaces
│   ├── utils/            # Utility functions
├── Simulacra/            # Backend support
├── MedPromptSimulate/    # Dignosis memory support
├── examples/             # Example scenarios and configurations
├── tests/                # Unit and integration tests. Coming soon
├── requirements.txt      # Python dependencies
├── LICENSE               # License information
└── README.md             # This file
```

## 🛠️ Development

### Implementing a New Model

```python
coming soon!
```
## 👥 Contributing

We welcome contributions to MedAgentSim! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0) - see [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/) for details.
## 📚 Citation

If you use MedAgentSim in your research, please cite our paper:

```bibtex
@inproceedings{almansooriandkumarMedAgentSim,
  title={Self-Evolving Multi-Agent Simulations for Realistic Clinical Interactions},
  author={Mohammad Almansoori and Komal Kumar and Hisham Cholakkal},
  booktitle={International Conference on Medical Image Computing and Computer-Assisted Intervention},
  year={2025}
}
```
## 🙏 Acknowledgements
- Thanks to [AgentClinic](https://github.com/samuelschmidgall/agentclinic), [Microsoft PromptBase](https://github.com/microsoft/promptbase), and [Generative Agents](https://github.com/joonspk-research/generative_agents) for open-sourcing their works
- Mohamed bin Zayed University of Artificial Intelligence for supporting this research
- We encourage you to support the following three talented artists whose assets were used in this project, especially if you are planning to use the assets included here for your own project: 
  * Background art: [PixyMoon (@_PixyMoon\_)](https://twitter.com/_PixyMoon_)
  * Furniture/interior design: [LimeZu (@lime_px)](https://twitter.com/lime_px)
  * Character design: [ぴぽ (@pipohi)](https://twitter.com/pipohi)
## Other Resources
- Open-source multi-agent framework: [CAMEL-AI OWL](https://github.com/camel-ai/owl)
- Multi-agent framework: [OpenMANAUS](https://github.com/mannaandpoem/OpenManus)
- MedPrompt Blog: [The Power of Prompting](https://www.microsoft.com/en-us/research/blog/the-power-of-prompting/)
- MedPrompt Research Paper: [https://arxiv.org/abs/2311.16452](https://arxiv.org/abs/2311.16452)
- MedPrompt+: [Steering at the Frontier: Extending the Power of Prompting](https://www.microsoft.com/en-us/research/blog/steering-at-the-frontier-extending-the-power-of-prompting/)
- Microsoft Introduction to Prompt Engineering: [https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering)
- Microsoft Advanced Prompt Engineering Guide: [https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/advanced-prompt-engineering?pivots=programming-language-chat-completions](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/advanced-prompt-engineering?pivots=programming-language-chat-completions)

## 📞 Contact

For questions or support, please open an issue or contact the maintainers:

- GitHub: [@MAXNORM8650](https://github.com/MAXNORM8650)

---

Made with ❤️ by the MedAgentSim Team
