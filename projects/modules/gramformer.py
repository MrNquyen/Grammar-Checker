from gramformer import Gramformer
import torch

class GramFormerChecker:
    def __init__(self):
        self.set_seed(1212)

    def set_seed(seed):
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def load_model(self):
        self.model = Gramformer(models = 1, use_gpu=False) # 1=corrector, 2=detector

    def correct_text(self, text, max_candidates=5)-> list:
        corrected_sentences: list = self.model.correct(text, max_candidates=max_candidates)
        return corrected_sentences

    def correct_batch(self, texts, max_candidates=5)-> list:
        batch_corrected_sentences = []
        for text in texts:
            corrected_sentences = self.correct_text(text, max_candidates)
            batch_corrected_sentences.append(corrected_sentences)
        return batch_corrected_sentences
