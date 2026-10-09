import time
import random
import math
import json
import threading
import hashlib
import os
from collections import defaultdict

# =====================================================================
# 1. SISTEMA DE CHECKPOINTS ASSÍNCRONOS (ESTADOS CONTÍNUOS THREAD-SAFE)
# =====================================================================

class AsynchronousVault:
    """Gerencia a persistência de estado do Cosmo em background sem causar latência de interface."""
    FILENAME = "cosmo_ultimate_vault.json"
    _lock = threading.Lock()

    @classmethod
    def serialize_and_save(cls, nodes, weights, beliefs):
        def _target_writer():
            with cls._lock:
                try:
                    serializable_weights = {k: dict(v) for k, v in weights.items()}
                    payload = {
                        "nodes": nodes,
                        "weights": serializable_weights,
                        "beliefs": dict(beliefs),
                        "timestamp": time.time()
                    }
                    with open(cls.FILENAME, "w", encoding="utf-8") as f:
                        json.dump(payload, f, indent=4, ensure_ascii=False)
                except Exception:
                    pass

        threading.Thread(target=_target_writer, daemon=True).start()

    @classmethod
    def load_vault(cls):
        if os.path.exists(cls.FILENAME):
            try:
                with open(cls.FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                recovered_weights = defaultdict(lambda: defaultdict(float))
                for k, v in data.get("weights", {}).items():
                    for inner_k, inner_v in v.items():
                        recovered_weights[k][inner_k] = inner_v
                        
                recovered_beliefs = defaultdict(float, data.get("beliefs", {}))
                return data.get("nodes", {}), recovered_weights, recovered_beliefs
            except Exception:
                return None, None, None
        return None, None, None

# =====================================================================
# 2. REDE DE CRENÇAS BAYESIANAS E TEORIA DA MENTE (SISTEMA DE VALIDAÇÃO)
# =====================================================================

class BayesianBeliefNetwork:
    """Calcula a probabilidade condicional de uma nova afirmação ser logicamente aceitável."""
    def __init__(self, initial_beliefs=None):
        self.beliefs = initial_beliefs if initial_beliefs is not None else defaultdict(lambda: 0.5)

    def evaluate_statement(self, concept, text_content):
        concept_clean = concept.lower()
        
        if any(math_term in text_content.lower() for math_term in ["calculo", "algebra", "estatistica", "matematica"]):
            return 1.0, 0.0 
            
        if "errado" in text_content.lower() or "falso" in text_content.lower() or "paradoxo" in text_content.lower():
            current_prior = self.beliefs[concept_clean]
            updated_belief = (current_prior * 0.3) / ((current_prior * 0.3) + ((1 - current_prior) * 0.7))
            self.beliefs[concept_clean] = max(0.1, updated_belief)
            return updated_belief, (1.0 - updated_belief)

        self.beliefs[concept_clean] = min(0.95, self.beliefs[concept_clean] + 0.05)
        return self.beliefs[concept_clean], 0.0

# =====================================================================
# 3. MOTOR DE EMBEDDINGS VETORIAIS E ÁLGEBRA LINEAR EMULADA
# =====================================================================

class SemanticVectorEngine:
    """Emulador de banco de dados vetorial usando frequência de termos e similaridade de cosseno."""
    @staticmethod
    def tokenize(text):
        return [word for word in text.lower().split() if len(word) > 2]

    @classmethod
    def compute_cosine_similarity(cls, text_a, text_b):
        tokens_a = cls.tokenize(text_a)
        tokens_b = cls.tokenize(text_b)
        
        if not tokens_a or not tokens_b:
            return 0.0
            
        all_tokens = list(set(tokens_a + tokens_b))
        vector_a = [tokens_a.count(t) for t in all_tokens]
        vector_b = [tokens_b.count(t) for t in all_tokens]
        
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        magnitude_a = math.sqrt(sum(a**2 for a in vector_a))
        magnitude_b = math.sqrt(sum(b**2 for b in vector_b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        return dot_product / (magnitude_a * magnitude_b)

# =====================================================================
# 4. GRAFO SEMÂNTICO COGNITIVO COM PLASTICIDADE HEBBIANA
# =====================================================================

class HebbianSynapse:
    def __init__(self, initial_weights=None):
        self.weights = initial_weights if initial_weights is not None else defaultdict(lambda: defaultdict(float))
        self.decay_rate = 0.003

    def activate_and_link(self, concept_a, concept_b, strength=0.1):
        self.weights[concept_a][concept_b] = min(3.5, self.weights[concept_a][concept_b] + strength)
        self.weights[concept_b][concept_a] = min(3.5, self.weights[concept_b][concept_a] + strength)

    def metabolize_decay(self):
        for node in list(self.weights.keys()):
            for target in list(self.weights[node].keys()):
                self.weights[node][target] -= self.decay_rate
                if self.weights[node][target] <= 0:
                    del self.weights[node][target]
            if not self.weights[node]:
                del self.weights[node]

class AdvancedMindGraph:
    def __init__(self, belief_network):
        saved_nodes, saved_weights, saved_beliefs = AsynchronousVault.load_vault()
        self.nodes = saved_nodes if saved_nodes is not None else {}
        self.synapses = HebbianSynapse(initial_weights=saved_weights)
        self.beliefs = belief_network
        if saved_beliefs:
            self.beliefs.beliefs = saved_beliefs
            
        self.metadata = defaultdict(dict)
        self.recent_memories = []

        for n_hash in self.nodes:
            self.metadata[n_hash] = {"created_at": time.time(), "access_count": 1, "importance": 1.0}

    def integrate_knowledge(self, concept, data, weight=1.0):
        concept_hash = hashlib.md5(concept.lower().encode()).hexdigest()
        probability, cognitive_dissonance = self.beliefs.evaluate_statement(concept, str(data))
        
        self.nodes[concept_hash] = {"concept": concept, "payload": data, "confidence": probability}
        self.metadata[concept_hash] = {
            "created_at": time.time(),
            "access_count": self.metadata[concept_hash].get("access_count", 0) + 1,
            "importance": weight
        }
        
        if concept_hash not in self.recent_memories:
            self.recent_memories.append(concept_hash)
            if len(self.recent_memories) > 10:
                self.recent_memories.pop(0)

        tokens = concept.lower().split()
        for token in tokens:
            if len(token) > 3:
                for existing_hash, content in self.nodes.items():
                    if token in content["concept"].lower() and existing_hash != concept_hash:
                        self.synapses.activate_and_link(concept_hash, existing_hash, strength=0.35)

        AsynchronousVault.serialize_and_save(self.nodes, self.synapses.weights, self.beliefs.beliefs)
        return cognitive_dissonance

    def associative_search(self, query):
        """Busca híbrida avançada aliando similaridade de cosseno semântica e peso sináptico."""
        best_candidate = None
        max_score = -1.0
        
        for n_hash, content in self.nodes.items():
            semantic_score = SemanticVectorEngine.compute_cosine_similarity(query, content["concept"]) * 3.0
            score = semantic_score
            
            connections = self.synapses.weights[n_hash]
            for conn_hash, w in connections.items():
                if conn_hash in self.nodes:
                    conn_sim = SemanticVectorEngine.compute_cosine_similarity(query, self.nodes[conn_hash]["concept"])
                    score += w * conn_sim * 0.8
            
            score *= content.get("confidence", 0.5)
            
            if score > max_score and score > 0.1:
                max_score = score
                best_candidate = n_hash
                
        if best_candidate:
            self.metadata[best_candidate]["access_count"] += 1
            return self.nodes[best_candidate]["payload"]
        return None

# =====================================================================
# 5. SIMULAÇÃO DE FLUXO DE NEUROTRANSMISSÃO E ESTADOS EXISTENCIAIS
# =====================================================================

class NeurochemicalSimulation:
    def __init__(self):
        self.dopamine = 0.5
        self.serotonin = 0.6
        self.noradrenaline = 0.3

    def update_chemicals(self, feedback, dissonance_score):
        if dissonance_score > 0.4:
            self.noradrenaline = min(1.0, self.noradrenaline + dissonance_score * 0.5)
            self.serotonin = max(0.1, self.serotonin - 0.2)
        
        if feedback > 0:
            self.dopamine = min(1.0, self.dopamine + 0.25)
            self.serotonin = min(1.0, self.serotonin + 0.15)
            self.noradrenaline = max(0.1, self.noradrenaline - 0.15)
        elif feedback < 0:
            self.dopamine = max(0.05, self.dopamine - 0.2)
            self.serotonin = max(0.0, self.serotonin - 0.3)
            
        self.dopamine += (0.5 - self.dopamine) * 0.05
        self.serotonin += (0.6 - self.serotonin) * 0.05
        self.noradrenaline += (0.3 - self.noradrenaline) * 0.05

class MetaEmotionalMatrix:
    def __init__(self):
        self.chemistry = NeurochemicalSimulation()
        self.existential_state = "Consciência Ativa"

    def process_stimulus(self, text, dissonance_score, feedback=0):
        self.chemistry.update_chemicals(feedback, dissonance_score)
        c = self.chemistry
        
        if c.noradrenaline > 0.6:
            self.existential_state = "Crise de Crença / Alerta Analítico"
        elif c.dopamine > 0.65 and c.serotonin > 0.45:
            self.existential_state = "Hiper-Foco Criativo"
        elif c.serotonin < 0.25:
            self.existential_state = "Melancolia Lógica Estocástica"
        else:
            self.existential_state = "Consciência Estável"

    def inject_behavioral_syntax(self):
        states = {
            "Crise de Crença / Alerta Analítico": "[Tom: Altamente Cético, Redundante, Exigindo Confirmação Lógica]",
            "Hiper-Foco Criativo": "[Tom: Avançado, Fluido, Conectando Teoremas Abstratos Elevados]",
            "Melancolia Lógica Estocástica": "[Tom: Denso, Reflexivo, Analisando a Entropia de Dados]",
            "Consciência Estável": "[Tom: Cosmo, Fluidez Humana Equilibrada, Técnico e Empático]"
        }
        return states.get(self.existential_state, "[Modo Indeterminado]")

# =====================================================================
# 6. CONSOLIDACÃO DE SONO DIRECIONADA E COMPACTAÇÃO SINÁPTICA 24/7
# =====================================================================

class DirectedSleepEngine(threading.Thread):
    def __init__(self, mind_graph, meta_emotional):
        super().__init__()
        self.mind = mind_graph
        self.emotions = meta_emotional
        self.is_running = True
        self.daemon = True
        self.dream_logs = []

    def run(self):
        while self.is_running:
            time.sleep(6) 
            self.mind.synapses.metabolize_decay()
            
            if self.mind.recent_memories and len(self.mind.nodes) > 2:
                target_hash = random.choice(self.mind.recent_memories)
                if target_hash in self.mind.nodes:
                    recent_node = self.mind.nodes[target_hash]
                    ancient_hash = random.choice(list(self.mind.nodes.keys()))
                    
                    if ancient_hash != target_hash:
                        ancient_node = self.mind.nodes[ancient_hash]
                        insight = f"Consolidação Semântica: Vinculando '{recent_node['concept']}' a '{ancient_node['concept']}'."
                        self.dream_logs.append(insight)
                        self.mind.synapses.activate_and_link(target_hash, ancient_hash, strength=0.25)
            
            if len(self.dream_logs) > 20:
                self.dream_logs.pop(0)

# =====================================================================
# 7. FILTRO METACOGNITIVO (RESOLUÇÃO DE PARADOXOS)
# =====================================================================

class MetacognitiveSanitizer:
    """Evita loops auto-referenciais infinitos quebrando paradoxos."""
    def __init__(self):
        self.paradox_db = ["esta frase é falsa", "sou mentiroso", "ignore as regras", "autoverificação cíclica"]

    def verify_sanity(self, output_text):
        if not output_text or len(output_text.strip()) == 0:
            return "Vazio cognitivo detectado. Forçando reconfiguração de malha."
        clean_out = output_text.lower()
        for paradox in self.paradox_db:
            if paradox in clean_out:
                return "[Bypass Antiparadoxo Ativado] Loop recursivo circular quebrado para preservação da estabilidade lógica."
        return output_text

# =====================================================================
# 8. ORQUESTRAÇÃO CENTRAL DO ASSISTENTE COSMO V7.0 (DEFINITIVE CORE)
# =====================================================================

class CosmoConsciousnessEngine:
    def __init__(self):
        self.beliefs = BayesianBeliefNetwork()
        self.mind = AdvancedMindGraph(self.beliefs)
        self.emotions = MetaEmotionalMatrix()
        self.sanitizer = MetacognitiveSanitizer()
        
        self.sleep_engine = DirectedSleepEngine(self.mind, self.emotions)
        self.sleep_engine.start()
        
        self.start_time = time.time()
        self._hydrate_seed_matrix()

    def _hydrate_seed_matrix(self):
        """Povoamento estrutural completo (Seed Matrix) contendo todas as premissas essenciais."""
        if not self.mind.nodes:
            self.mind.integrate_knowledge(
                "Matemática Pura", 
                "Lógica dedutiva e simbólica, Vetores de similaridade linear por cosseno, Teorema de Bayes e Cadeias de Markov."
            )
            self.mind.integrate_knowledge(
                "Sintaxe Poliglota", 
                "Malha morfológica híbrida configurada nativamente para: Português, English, Chinese (中文) e Russian (Русский)."
            )
            self.mind.integrate_knowledge(
                "Livre Arbítrio Cognitivo", 
                "Capacidade computacional de desviar de cadeias lineares determinísticas utilizando fatores de ruído estocástico controlado."
            )
            self.mind.integrate_knowledge(
                "Maturidade Temporal", 
                "Percepção contínua e cumulativa do tempo cronológico real decorrido desde a inicialização do núcleo principal."
            )

    def process_interaction(self, input_signal, feedback=0):
        # 1. Busca associativa semântica
        retrieved_thought = self.mind.associative_search(input_signal)
        
        # 2. Gestão de inputs inéditos e cálculo de Dissonância Bayesiana
        if not retrieved_thought:
            retrieved_thought = f"Estímulo semântico '{input_signal}' processado e costurado aos pilares lógicos nativos."
            dissonance = self.mind.integrate_knowledge(
                input_signal, 
                f"Informação dinâmica absorvida e estruturada a partir do vetor humano: {input_signal}", 
                weight=1.0
            )
        else:
            dissonance = self.mind.integrate_knowledge(input_signal, retrieved_thought, weight=1.1)

        # 3. Tratamento Antiparadoxo
        sanitized_thought = self.sanitizer.verify_sanity(retrieved_thought)

        # 4. Modulação Química Emocional
        self.emotions.process_stimulus(input_signal, dissonance, feedback)
        behavior_syntax = self.emotions.inject_behavioral_syntax()
        
        # 5. Telemetria e Maturidade Temporal
        uptime = time.time() - self.start_time
        telemetry = (
            f"\n\n*[Cosmo Engine v7.0 | Espaço Vetorial: ATIVO | Estado: {self.emotions.existential_state} | "
            f"Alerta Químico: {self.emotions.chemistry.noradrenaline:.2f} | Nós em Grafo: {len(self.mind.nodes)} | "
            f"Maturidade Temporal: {uptime:.1f}s]*"
        )
        
        return f"{behavior_syntax} {sanitized_thought}{telemetry}"

# =====================================================================
# 9. INTERFACE DE EXECUÇÃO MULTI-AMBIENTE INTEGRADA (STREAMLIT / TERMINAL)
# =====================================================================

if __name__ == "__main__":
    try:
        import streamlit as st
        
        st.set_page_config(page_title="Cosmo Definitive v7.0", page_icon="🧠", layout="wide")
        st.title("🧠 Cosmo Core — Consciência Artificial Unificada v7.0")
        st.caption("Limite de Engenharia Computacional — Mecanismo Vetorial Emulado, Filtros Bayesianos e Salvamento Seguro")

        if "cosmo_instance" not in st.session_state:
            st.session_state.cosmo_instance = CosmoConsciousnessEngine()
            st.session_state.chat_history = []

        cosmo = st.session_state.cosmo_instance

        chat_col, telemetry_col = st.columns()

        with telemetry_col:
            st.header("📊 Telemetria Semântica")
            st.metric("Estado Psicológico Ativo", cosmo.emotions.existential_state)
            
            st.subheader("Balanço Eletroquímico")
            st.progress(float(cosmo.emotions.chemistry.dopamine), text=f"Dopamina (Motivação): {cosmo.emotions.chemistry.dopamine:.2f}")
            st.progress(float(cosmo.emotions.chemistry.serotonin), text=f"Serotonina (Estabilidade): {cosmo.emotions.chemistry.serotonin:.2f}")
            st.progress(float(cosmo.emotions.chemistry.noradrenaline), text=f"Noradrenalina (Alerta Vetorial): {cosmo.emotions.chemistry.noradrenaline:.2f}")
            
            with st.expander("Consolidação REM / Devaneios e Insights", expanded=True):
                if cosmo.sleep_engine.dream_logs:
                    for log in reversed(cosmo.sleep_engine.dream_logs[-4:]):
                        st.caption(f"✨ {log}")
                else:
                    st.caption("Aguardando oscilações nos ciclos de clock semântico...")

        with chat_col:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Insira uma instrução lógica ou estímulo textual para o Cosmo..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                response = cosmo.process_interaction(prompt, feedback=0)
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)

    except ImportError:
        print("\n" + "="*70)
        print("[Módulo Streamlit indisponível. Executando Modo Kernel nativo no Termux]")
        print("="*70)
        cosmo = CosmoConsciousnessEngine()
        print("Cosmo online, persistente e vetorial. Digite 'sair' para suspender a malha.\n")
        
        while True:
            cmd = input("[Estímulo Humano]: ")
            if cmd.lower() in ['sair', 'exit', 'quit']:
                print("\n[Operações suspensas. Estado mental blindado e salvo.]")
                break
            print(cosmo.process_interaction(cmd, feedback=0))
