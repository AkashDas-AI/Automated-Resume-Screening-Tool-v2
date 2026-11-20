"""
Similarity Computation Module
Author: Akash Das
Project: Automated Resume Screening Tool

Responsible for generating TF-IDF vector representations and calculating
deterministic cosine similarity between job descriptions and candidate resumes
using Scikit-learn on a unified, consistent corpus.
"""

from typing import Tuple, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.text_cleaner import strip_personal_identifiers


def get_default_vectorizer() -> TfidfVectorizer:
    """
    Instantiate a TfidfVectorizer with deterministic, technical-token-safe settings:
    - ngram_range=(1, 2): captures unigrams and bigrams.
    - stop_words='english': filters non-technical stopwords.
    - token_pattern: preserves technical symbols (+, #, ., -, /).
    """
    return TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        token_pattern=r"(?u)\b[a-zA-Z0-9\.\+#\-/]+\b"
    )


class TFIDFSimilarityEngine:
    """
    Consistent corpus-level TF-IDF similarity model.

    Fits once on the complete document collection (1 Job Description + N Resumes),
    guaranteeing that all candidates are evaluated against the exact same vocabulary
    and IDF weights.
    """

    def __init__(self, job_description: str, resumes: List[str], sanitize: bool = True):
        """
        Initialize and fit the similarity engine on the unified corpus.

        Args:
            job_description (str): Cleaned target job description text.
            resumes (List[str]): List of cleaned candidate resume texts.
            sanitize (bool): Whether to strip personal identifiers (names, emails, phones)
                prior to vectorization. Defaults to True.
        """
        if not isinstance(job_description, str):
            raise TypeError("job_description must be a string.")
        if not isinstance(resumes, list):
            raise TypeError("resumes must be a list of strings.")

        self.sanitize = sanitize
        self.sanitized_jd = strip_personal_identifiers(job_description) if sanitize else job_description
        self.sanitized_resumes = [
            strip_personal_identifiers(r) if sanitize else r for r in resumes
        ]

        # Shared corpus: Job Description at index 0, followed by candidate resumes
        self.corpus = [self.sanitized_jd] + self.sanitized_resumes
        self.vectorizer = get_default_vectorizer()

        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
            self.jd_vector = self.tfidf_matrix[0:1]
            self.resume_vectors = self.tfidf_matrix[1:]
        except ValueError:
            # Empty vocabulary fallback
            self.tfidf_matrix = None
            self.jd_vector = None
            self.resume_vectors = None

    def get_similarities(self) -> List[float]:
        """
        Calculate cosine similarity between the job description and every candidate resume.

        Returns:
            List[float]: Cosine similarities in the same order as the input resumes,
                strictly bounded in [0.0, 1.0].
        """
        if self.tfidf_matrix is None or len(self.sanitized_resumes) == 0:
            return [0.0] * len(self.sanitized_resumes)

        sim_matrix = cosine_similarity(self.jd_vector, self.resume_vectors)
        sim_scores = sim_matrix[0]
        return [float(np.clip(s, 0.0, 1.0)) for s in sim_scores]

    def transform_text_similarity(self, text: str) -> float:
        """
        Transform a single document using the pre-fitted vectorizer and compute
        its cosine similarity against the job description vector.
        """
        if self.tfidf_matrix is None or not text.strip():
            return 0.0

        sanitized = strip_personal_identifiers(text) if self.sanitize else text
        vec = self.vectorizer.transform([sanitized])
        sim = float(cosine_similarity(self.jd_vector, vec)[0][0])
        return float(np.clip(sim, 0.0, 1.0))


def compute_corpus_similarities(
    job_description: str,
    resumes: List[str],
    sanitize: bool = True
) -> List[float]:
    """
    Convenience function to fit on a complete corpus and return all resume similarities.

    Args:
        job_description (str): Target job description text.
        resumes (List[str]): Candidate resume texts.
        sanitize (bool): Whether to exclude personal identifiers. Defaults to True.

    Returns:
        List[float]: List of similarity values corresponding to each candidate.
    """
    engine = TFIDFSimilarityEngine(job_description, resumes, sanitize=sanitize)
    return engine.get_similarities()


def calculate_similarity(
    job_description: str,
    resume_text: str,
    vectorizer: Optional[TfidfVectorizer] = None,
    sanitize: bool = True
) -> float:
    """
    Compute TF-IDF cosine similarity between job description text and resume text.

    If a pre-fitted vectorizer is provided, transforms both documents using that vectorizer.
    Otherwise, fits a vectorizer on the two-document pair as a single-evaluation fallback.

    Args:
        job_description (str): Target job description text.
        resume_text (str): Candidate resume text.
        vectorizer (Optional[TfidfVectorizer]): Pre-fitted corpus vectorizer.
        sanitize (bool): Whether to strip personal identifiers. Defaults to True.

    Returns:
        float: Cosine similarity score bounded in [0.0, 1.0].
    """
    if not isinstance(job_description, str):
        raise TypeError(f"job_description must be str, got {type(job_description).__name__}.")
    if not isinstance(resume_text, str):
        raise TypeError(f"resume_text must be str, got {type(resume_text).__name__}.")

    jd_clean = strip_personal_identifiers(job_description) if sanitize else job_description
    res_clean = strip_personal_identifiers(resume_text) if sanitize else resume_text

    if not jd_clean.strip() or not res_clean.strip():
        return 0.0

    if vectorizer is not None:
        try:
            jd_vec = vectorizer.transform([jd_clean])
            res_vec = vectorizer.transform([res_clean])
            sim = float(cosine_similarity(jd_vec, res_vec)[0][0])
            return float(np.clip(sim, 0.0, 1.0))
        except ValueError:
            return 0.0

    # Fallback pairwise fit
    vec = get_default_vectorizer()
    try:
        matrix = vec.fit_transform([jd_clean, res_clean])
    except ValueError:
        return 0.0

    sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    return float(np.clip(sim, 0.0, 1.0))


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Backward compatibility alias."""
    return calculate_similarity(jd_text, resume_text)


def vectorize_documents(documents: List[str]) -> Tuple[TfidfVectorizer, np.ndarray]:
    """Fit and transform documents using default vectorizer."""
    if not isinstance(documents, list):
        raise TypeError(f"vectorize_documents expected list, got {type(documents).__name__}.")
    if not documents:
        raise ValueError("Cannot vectorize an empty document list.")

    vec = get_default_vectorizer()
    mat = vec.fit_transform(documents)
    return vec, mat
