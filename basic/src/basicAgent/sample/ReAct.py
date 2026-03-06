import re
import os
from basicAgent.utils.HelloAgentsLLM import HelloAgentsLLM
from basicAgent.utils.Tool import ToolExecutor
from jinja2 import Environment, FileSystemLoader
from basicAgent.tools.WebSearch import search


# 设置模板环境（指定模板文件所在目录）


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "../../../config/prompts")))


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        运行ReAct智能体来回答一个问题。
        """
        self.history = []
        current_step = 0

        while current_step<self.max_steps:
            current_step+=1
            print('\n\n')
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools() #获取工具
            history_str = "\n".join(self.history)

            template = env.get_template("ReAct.j2") # 读取prompt
            prompt = template.render({
                "tools": tools_desc,
                "question": question,
                "history": history_str
            })

            # 2. 调用LLM进行思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误:LLM未能返回有效响应。")
                break
                
            # 3. 解析LLM的输出
            thought, action = self._parse_output(response_text)
            
            # if thought:
            #     print(f"思考: {thought}")

            if not action:
                print("警告:未能解析出有效的Action，流程终止。")
                break

            # 4. 执行Action
            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print('\n\n')
                print(f"🎉 最终答案: {final_answer}")
                print('\n\n')
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... 处理无效Action格式 ...
                continue

            print(f"🎬 行动: {tool_name}[{tool_input}]")
            
            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input) # 调用真实工具
            
            print(f"👀 观察: {observation}")
            # 将本轮的Action和Observation添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # 循环结束
        print("已达到最大步数，流程终止。")
        return None


    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。
        """
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None




if __name__ == '__main__':
    # template = env.get_template("ReAct.j2") # 读取prompt
    # prompt = template.render({
    #                 "tools": '1',
    #                 "question": 'question',
    #                 "history": 'history'
    #             })
    # print(prompt)
    llm_client = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    tool_executor.registerTool("Search", search_description, search)
    agent = ReActAgent(llm_client=llm_client, tool_executor=tool_executor)
    agent.run("请告诉我今天广州的天气。")