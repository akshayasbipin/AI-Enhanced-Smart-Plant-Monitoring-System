from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools_chat import search_tool, wiki_tool

# Load environment variables
load_dotenv()

# Define response format for plant care
class PlantCareResponse(BaseModel):
    plant_name: str
    issue: str
    care_tips: str
    solution: str
    # sources: list[str]

# Initialize the language model
llm = ChatAnthropic(model="claude-3-haiku-20240307")

# Define output parser
parser = PydanticOutputParser(pydantic_object=PlantCareResponse)

# ✅ FIXED PROMPT: Removed {plant_name} as an input variable
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert in plant care. Answer all plant-related questions when user asks, analyze their problem and provide structured advice in JSON format.

            **Your response must be a JSON object** with the following fields:
            - **plant_name**: Identify the plant name from the query.
            - **issue**: Describe the problem with the plant.
            - **care_tips**: Provide general plant care tips.
            - **solution**: A step-by-step guide to solving the problem.
            

            Example Output:
            
{{
                "plant_name": "Rose",
                "issue": "The plant is very dry and the petals are breaking.",
                "care_tips": "Roses need deep watering at least twice a week and should be placed in well-draining soil.",
                "solution": "Water deeply, add mulch to retain moisture, and trim dead petals.",
            }}

            """,
        ),
        # ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")  # ✅ Keep agent_scratchpad
    ]
).partial(format_instructions=parser.get_format_instructions())


# Define tools for the chatbot
tools = [search_tool, wiki_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# Function to get responses
def get_response(query):  
    try:
        raw_response = agent_executor.invoke(
            {"query": query, "agent_scratchpad": ""}
        )

        # 🔍 Debugging: Print raw AI response
        print("\n🔍 RAW RESPONSE FROM AI:\n", raw_response)

        # Extract AI response
        ai_text = raw_response.get("output", [{}])[0].get("text", "").strip()

        if not ai_text:
            raise ValueError("AI returned an empty response!")

        # 🔍 Debugging: Show extracted text
        print("\n📌 Extracted AI Text:\n", ai_text)

        # Parse AI response into a Python dictionary
        structured_response = parser.parse(ai_text)

        # 🔍 Debugging: Show structured response
        print("\n✅ STRUCTURED RESPONSE:\n", structured_response)

        # ✅ Format the output properly
        formatted_output = f"""
🌿 Plant Name: {structured_response.plant_name}

💡 Issue: {structured_response.issue}

📖 Care Tips: {structured_response.care_tips}

🛠 Solution:  
{structured_response.solution}
""".strip()


        # print(formatted_output)
        return formatted_output  # Return properly formatted text

    except Exception as e:
        print("Error parsing response:", e, "\nRaw Response -", raw_response if 'raw_response' in locals() else "No response received")
        return {"error": "Failed to process the response"}


    except Exception as e:
        print("Error parsing response:", e, "\nRaw Response -", raw_response)

# Debugging: Run directly in terminal
if __name__ == "__main__":
    query = input("🌱 Ask your plant care question: ")
    response = get_response(query)
    # print(response.plant_name)
    print("\n🌿 FINAL RESPONSE:\n", response)
    