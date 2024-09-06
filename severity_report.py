from langchain_ollama import OllamaLLM


model = OllamaLLM(model='llama3.1')


def predict_diseases(symptoms):

    input_prompt = f"""You are an AI assistant designed to help diagnose potential health issues based on reported symptoms. 
    Your goal is to analyze the provided symptoms and suggest possible diagnoses along with severity levels. 
    Based on the symptoms: {symptoms}, please follow these steps:
    
    1. Read through the symptoms carefully and think through potential diagnoses. 
    2. Provide your assessment in the following format:
       The most likely diagnosis based on the symptoms is: [DIAGNOSIS]   
       The severity level is: [RED/ORANGE/YELLOW/BLUE/GREEN]   
        [RECOMMENDED ACTIONS BASED ON SEVERITY LEVEL GUIDELINES PROVIDED BELOW]  
    
    Severity Level Guidelines:  
    RED (80-100): Rush to the hospital immediately.  
    ORANGE (60-80): Consult a doctor or visit a 'Mohalla Clinic' soon and follow basic remedies until then.  
    YELLOW (40-60): Visit a 'Mohalla Clinic' or take an online consultation.  
    BLUE (20-40): Mild issue. Suggest home remedies.  
    GREEN (0-20): No significant health problem, no medical visit required.  
    
    3. If no diagnosis can be made based on the symptoms, state that clearly."""
    
    result = model.invoke(input=input_prompt)
    diseases = result

    return diseases
def health_chatbot():
    while True:
        symptoms = input("Please enter your symptoms (or type 'bye' to exit): ")
        if symptoms.lower() == "bye":
            print("Goodbye! Take care.")
            break

        possible_diseases = predict_diseases(symptoms)
        
        print("Based on your symptoms, here is the assessment:")
        print(possible_diseases)

health_chatbot()
