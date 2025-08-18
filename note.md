_-------_
" & d:/working/freelance/learning/langchain/.venv/Scripts/Activate.ps1"
" Select interpreter "
**def** keyword is used to define a function
https://excalidraw.com/#json=GUDuovTlyCegUiAFCPClu,D5ciMUb6KmrWKzlpWHMKXA

<!-- TODO -->

read and follow the example: 
  + https://github.com/langchain-ai/langchain-academy/blob/main/module-2/trim-filter-messages.ipynb
  + https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/
  + https://langchain-ai.github.io/langgraph/concepts/multi_agent/#communication-and-state-management
  + https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/#7-assemble-the-graph
```python
def function_name(parameters):
      """Optional docstring explaining the function."""
    # function body (indented)
    # do something
    return result  # optional
```

- basic ✅
- basic search tools ✅
- agent ✅
  _-------_

_-------_

# DOC and notes:

_Key Components of langgraph_
**State**
declared the shape state object, using a Python TypedDict. This acts as a schema for your application's memory, defining what information will be tracked `(e.g., user's question, retrieved documents, conversation history)`.

```python
class State(TypedDict):
    graph_state: str
```

- **Nodes** :
- Python function
- Each node operates on the the state
- Default, each node will `override` the prior state value

```python
  def node_1(state):
      return state["graph_state"] + "node_1 state"

  def node_1(state):
      return state["graph_state"] + "node_2 state override"

```

- **Edges** : connections that define the workflow, define the path from one node to the next, allow to route the flow based on the contents of the state, enabling true decision-making.

```python
class State(dict):
    pass

# Khởi tạo graphx
workflow = StateGraph(State)

# Node đầu tiên
def start(state: State):
    return {"value": state.get("input")}

workflow.add_node("start", start)

# Node xử lý thành công
def success(state: State):
    print("Success branch executed!")
    return state

workflow.add_node("success", success)

# Node xử lý thất bại
def failure(state: State):
    print("Failure branch executed!")
    return state

workflow.add_node("failure", failure)

# Thêm cạnh có điều kiện
def condition(state: State):
    if state["value"] == "ok":
        return "success"
    return "failure"

workflow.add_conditional_edges(
    "start",   # node nguồn
    condition, # hàm điều kiện
    {          # ánh xạ giá trị -> node đích
        "success": "success",
        "failure": "failure",
    }
)

# Xác định node bắt đầu & kết thúc
workflow.set_entry_point("start")
workflow.add_edge("success", END)
workflow.add_edge("failure", END)

# Biên dịch
app = workflow.compile()

# Test
app.invoke({"input": "ok"})       # -> chạy vào success
app.invoke({"input": "not ok"})   # -> chạy vào failure

```

_-------_

_-------_

## Syntax

## Breaking Down the Syntax

Here is the line of code: `def human_assistance(query: str) -> str:`

`(query: str)`: This part defines the function's parameters (the inputs it needs).

-> str: This is the return type hint.

The arrow `->` indicates that we're specifying what the function will return.

`str` makes a promise that this function's _final output will always be a str_.

## What assert Does in Python

The `assert` keyword is a debugging aid. It tests if a condition is True.

```python
assert len(message.tool_calls) <= 1
```

If the condition is True, your program continues to run without interruption.

If the condition is False, it immediately stops the program and raises an AssertionError.

It's a way for a developer to state, "I am absolutely sure this condition should be true at this point. If it's not, my logic is flawed, and the program should stop immediately so I can fix it."

_-------_
