FROM continuumio/miniconda3:24.7.1-0

# Create a conda environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Activate the Conda environment
RUN echo "conda activate projectenv" >> /etc/profile.d/conda.sh
ENV PATH="/opt/conda/envs/projectenv/bin:${PATH}"

RUN mkdir -p /run/jupyter && chown -R 1000:1000 /run/jupyter
ENV JUPYTER_RUNTIME_DIR=/run/jupyter

# Create a non-root user and switch to that user
RUN useradd -m projectuser && chown -R projectuser:projectuser /home/projectuser
USER projectuser

# Set working directory, and copy files
WORKDIR /home/projectuser

# Expose the JupyterLab
EXPOSE 8888

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--ServerApp.runtime_dir=/run/jupyter", "--ServerApp.cookie_secret_file=/run/jupyter/jupyter_cookie_secret"]
