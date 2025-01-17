from firestore_utils import firestore_save
from utils import get_oauth_uid
from chat_utils import generate_conversation_title, generate_stream


def save_messages_to_firestore(st, usage=None):
    messages = st.session_state["messages"]
    model = st.session_state["model"]

    if len(messages) > 0:
        conversation = st.session_state.get("conversation", {})
        title = conversation.get("title", None)
        if title is None:
            title = generate_conversation_title(messages)
        # get google uid from user_info object
        uid = get_oauth_uid(st)

        conversation_record = {
            "messages": messages,
            "usage": usage,
            "model_name": model,
            "title": title,
            "uid": uid,
        }

        cid = st.session_state.get("cid", None)

        # store conversations to firestore
        new_conversation = firestore_save(cid, conversation_record)
        print(new_conversation)
        return new_conversation


def render_chat_stream(st):
    with st.form(key="chat_prompt", clear_on_submit=True):
        # generate response stream here
        stream_holder = st.empty()

        user_input = st.text_area(
            f"You:", key="text_area_stream", label_visibility="collapsed"
        )
        submit_holder = st.empty()
        generating = st.session_state.get("generating", False)
        if generating:
            submit_button = submit_holder.form_submit_button(
                label="Generating...", disabled=True
            )
        else:
            submit_button = submit_holder.form_submit_button(label="Send")

    if submit_button and user_input:
        st.session_state["generating"] = True
        submit_holder.empty()
        st.session_state["conversation_expanded"] = False
        generate_stream(st, stream_holder, user_input)
        new_conversation = save_messages_to_firestore(st)
        st.session_state["generating"] = False
        if new_conversation is not None:
            st.session_state["cid"] = new_conversation.id
            st.experimental_rerun()
