"""Message classes."""

from abc import ABC
from abc import abstractmethod
from typing import Any
import pandas as pd
import streamlit as st
from pydantic import BaseModel
from pydantic import Field
from ai_stream import ASSISTANT_LABEL
from ai_stream import USER_LABEL
from ai_stream.components.tools import Tool
from ai_stream.components.tools import register_tool


# Message registry to keep track of all message types
message_registry: dict[str, Any] = {}


def register_message(cls):
    """Register message classes."""
    message_registry[cls.__name__] = cls
    return cls


class Message(Tool, ABC):
    """Base class for messages."""

    content: str | None = Field(None)

    def _run(self) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        """Render the message."""
        pass


@register_message
class UserMessage(Message):
    """User message."""

    def render(self) -> None:
        """Render the user message as text."""
        with st.chat_message(USER_LABEL):
            st.write(self.content)


@register_message
class AssistantMessage(Message):
    """Assistant message."""

    def render(self) -> None:
        """Render the assistant message as text."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.content)


class InputWidget(Message):
    """Base class for assistant messages with input widgets."""

    widget_config: dict[str, Any]
    key: str
    value: Any = None
    disabled: bool = False
    block_chat_input: bool = False

    def disable(self) -> None:
        """Disable input."""
        self.disabled = True

    @abstractmethod
    def render(self) -> None:
        """Render the input widget."""
        pass


@register_message
@register_tool
class TextInput(InputWidget):
    """Assistant message with a text input widget."""

    class TextInputSchema(BaseModel):
        """Schema for TextInput."""

        label: str = Field(..., description="A short label explaining the input.")
        value: str | None = Field("", description="The initial text value of the input.")
        max_chars: int | None = Field(None, description="Maximum number of characters allowed.")
        key: str | int | None = Field(None, description="Unique key for the widget.")
        type: str | None = Field("default", description="Type of input: 'default' or 'password'.")
        help: str | None = Field(None, description="Tooltip displayed next to the input.")
        autocomplete: str | None = Field(
            None, description="Autocomplete attribute for the input element."
        )
        placeholder: str | None = Field(
            None, description="Placeholder text displayed when input is empty."
        )
        disabled: bool | None = Field(False, description="Whether the input is disabled.")
        label_visibility: str | None = Field(
            "visible", description="Visibility of the label: 'visible', 'hidden', or 'collapsed'."
        )

    args_schema: type[BaseModel] = TextInputSchema
    name: str = "TextInput"
    description: str = "Tool for displaying a single-line text input widget."

    block_chat_input: bool = True

    def render(self) -> None:
        """Render the text input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.text_input(
                label="",
                value=self.value or "",
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class Selectbox(InputWidget):
    """Assistant message with a selectbox widget."""

    def render(self) -> None:
        """Render the selectbox widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            options = self.widget_config["options"]
            current_value = self.value if self.value in options else options[0]
            self.value = st.selectbox(
                label="",
                options=options,
                index=options.index(current_value),
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class Slider(InputWidget):
    """Assistant message with a slider widget."""

    def render(self) -> None:
        """Render the slider widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            default_value = self.widget_config.get("default", self.widget_config["min_value"])
            self.value = st.slider(
                label="",
                min_value=self.widget_config["min_value"],
                max_value=self.widget_config["max_value"],
                value=self.value if self.value is not None else default_value,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class Checkbox(InputWidget):
    """Assistant message with a checkbox widget."""

    def render(self) -> None:
        """Render the checkbox widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.checkbox(
                label="",
                value=self.value if self.value is not None else False,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class DateInput(InputWidget):
    """Assistant message with a date input widget."""

    def render(self) -> None:
        """Render the date input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.date_input(
                label="",
                value=self.value or None,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class TimeInput(InputWidget):
    """Assistant message with a time input widget."""

    def render(self) -> None:
        """Render the time input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.time_input(
                label="",
                value=self.value or None,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class NumberInput(InputWidget):
    """Assistant message with a number input widget."""

    def render(self) -> None:
        """Render the number input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            default_value = self.widget_config.get("default", self.widget_config["min_value"])
            self.value = st.number_input(
                label="",
                min_value=self.widget_config["min_value"],
                max_value=self.widget_config["max_value"],
                value=self.value if self.value is not None else default_value,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class TextArea(InputWidget):
    """Assistant message with a text area widget."""

    block_chat_input: bool = True

    def render(self) -> None:
        """Render the text area widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.text_area(
                label="",
                value=self.value or "",
                key=self.key,
                disabled=self.disabled,
            )


class OutputWidget(Message):
    """Base class for assistant messages with output widgets."""

    widget_data: Any

    @abstractmethod
    def render(self) -> None:
        """Render the output widget."""
        pass


@register_message
class LineChart(OutputWidget):
    """Assistant message that displays a line chart."""

    def render(self) -> None:
        """Render the line chart."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a line chart based on data:")
            chart_data = pd.DataFrame(self.widget_data)
            st.line_chart(chart_data)


@register_message
class BarChart(OutputWidget):
    """Assistant message that displays a bar chart."""

    def render(self) -> None:
        """Render the bar chart."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a bar chart based on data:")
            chart_data = pd.DataFrame(self.widget_data)
            st.bar_chart(chart_data)


@register_message
class Image(OutputWidget):
    """Assistant message that displays an image."""

    def render(self) -> None:
        """Render the image."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's an image:")
            st.image(
                self.widget_data["url"],
                caption=self.widget_data.get("caption", ""),
            )


@register_message
class Table(OutputWidget):
    """Assistant message that displays a table."""

    def render(self) -> None:
        """Render the table."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a table of data:")
            table_data = pd.DataFrame(self.widget_data)
            st.table(table_data)


@register_message
class Markdown(OutputWidget):
    """Assistant message that displays markdown content."""

    def render(self) -> None:
        """Render the markdown content."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's some formatted text:")
            st.markdown(self.widget_data["content"])
