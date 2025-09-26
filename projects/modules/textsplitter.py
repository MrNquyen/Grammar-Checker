from langchain.text_splitter import CharacterTextSplitter

class TextSplitter():
    def __init__(self):
        self.splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=0,
            keep_separator=True,
            strip_whitespace=True
        )

    def split_documents(self, docs):
        return self.splitter.split_text(docs)

