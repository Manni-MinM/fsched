use std::sync::Arc;

use axum::{
    extract::{Json, State},
    http::StatusCode,
    response::IntoResponse,
};
use serde::Deserialize;
use tokio::sync::Mutex;

use super::runtime::Runtime;

#[derive(Deserialize, Debug)]
pub struct HTTPRequest {
    adjustment: Option<i64>,
}

#[derive(Clone)]
pub struct HTTPService {
    pub runtime: Arc<Mutex<Runtime>>,
}

impl HTTPService {
    pub fn new(runtime: Runtime) -> Self {
        let runtime = Arc::new(Mutex::new(runtime));

        HTTPService {
            runtime,
        }
    }

    pub async fn info_handler(State(state): State<HTTPService>) -> impl IntoResponse {
        let mut runtime = state.runtime.lock().await;
        let info = runtime.export_info().await;

        Json(info).into_response()
    }

    pub async fn adjust_free_cache_handler(State(state): State<HTTPService>, Json(payload): Json<HTTPRequest>) -> impl IntoResponse {
        let mut runtime = state.runtime.lock().await;

        match payload.adjustment {
            Some(adjustment) => {
                match runtime.adjust_free_cache(adjustment).await {
                    Ok(_) => StatusCode::OK.into_response(),
                    Err(_) => StatusCode::INTERNAL_SERVER_ERROR.into_response(),
                }
            },
            _ => StatusCode::BAD_REQUEST.into_response()
        }
    }
}
