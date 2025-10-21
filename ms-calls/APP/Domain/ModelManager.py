class ModelManager:
    _instance = None
    _model= None
    _tokenizer=None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def get_model(self):
        if self._model is None or self._tokenizer is None:
            self._load_model()
        return self._tokenizer, self._model
    
    def _load_model(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        import logging
        from config import settings
        
        try:
            logging.info(f"Cargando modelo: {settings.ml_model_name}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(settings.ml_model_name)
            
            # Convertir string a tipo torch
            dtype_mapping = {
                "float16": torch.float16,
                "float32": torch.float32,
                "bfloat16": torch.bfloat16
            }
            
            self._model = AutoModelForCausalLM.from_pretrained(
                settings.ml_model_name,
                torch_dtype=dtype_mapping.get(settings.ml_model_dtype, torch.float16),
                device_map=settings.ml_model_device
            )
            
            logging.info("Modelo cargado exitosamente!")
            
        except Exception as e:
            logging.error(f"Error cargando modelo: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo: {e}")
        