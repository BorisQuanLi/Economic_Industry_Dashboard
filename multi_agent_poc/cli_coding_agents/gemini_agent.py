import sys
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import subprocess

# --- Configuration Constants ---
REGION = "us-central1"
MODEL_ID = "gemini-2.0-flash-001"
SYSTEM_INSTRUCTION = (
    "You are a senior Python engineer. Refactor code for readability, "
    "performance, and Docker compatibility."
)

def get_gcloud_project():
    """Dynamically retrieves the current gcloud project ID."""
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        # Fallback to environment variable if gcloud fails
        return os.getenv("GOOGLE_CLOUD_PROJECT")

def main():
    """
    Agent that uses the Vertex AI Python SDK to interact with Gemini 1.5 Pro.
    """
    if len(sys.argv) < 2:
        print("Usage: python gemini_agent.py \"<prompt>\"")
        sys.exit(1)

    prompt = sys.argv[1]
    
    # 1. Configuration
    # Using 'us-central1' which is a primary hub for Gemini 1.5 Pro
    PROJECT_ID = get_gcloud_project()
    REGION = "us-central1"
        
    # Use the specific version '002' to avoid 404s common with generic aliases
    MODEL_ID = "gemini-2.0-flash-001"

    if not PROJECT_ID:
        print("Error: Could not determine Project ID. Run 'gcloud config set project [ID]'")
        sys.exit(1)

    try:
        # 2. Initialize Vertex AI SDK
        # This handles authentication via Application Default Credentials (ADC)
        vertexai.init(project=PROJECT_ID, location=REGION)

        # 3. Initialize the Model
        model = GenerativeModel(MODEL_ID)

        # 4. Generate Content
        # We wrap this in a simple call to get the response text
        response = model.generate_content(prompt)

        # 5. Output results
        if response.text:
            print(response.text)
        else:
            print("Response received but no text content found.")

    except Exception as e:
        print(f"An error occurred while calling Vertex AI:")
        print(f"Details: {e}")
        print("\nTroubleshooting tips:")
        print(f"1. Ensure the API is enabled: 'gcloud services enable aiplatform.googleapis.com'")
        print(f"2. Ensure you have the 'Vertex AI User' role on project {PROJECT_ID}")
        print(f"3. Run 'gcloud auth application-default login' to refresh credentials")
        sys.exit(1)

if __name__ == "__main__":
    main()
