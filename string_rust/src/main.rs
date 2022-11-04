use actix_web::{get, web, App, HttpServer, Result, Responder};
use actix_web::web::Data;
use serde::Deserialize;
use serde::Serialize;
use edit_distance::edit_distance;

use mysql::*;
use mysql::prelude::Queryable;

#[derive(Debug, PartialEq, Eq)]
struct Stats {
    service: String,
    op: String,
    visits: i32,
}

#[derive(Deserialize)]
struct Params {
    a: String,
    b: String,
}

#[derive(Serialize)]
struct MyResult {
    res: String,
}

fn create_table(pool: &Pool) -> Result<(), mysql::Error> {
    let mut conn = pool.get_conn()?;
    conn.query_drop(r"CREATE TABLE IF NOT EXISTS stats (
        service VARCHAR(100) NOT NULL,
        op VARCHAR(100) NOT NULL,
        visits INT NOT NULL,
        primary key (service, op)
    )")?;
    Ok(())
}

//update stats for service and op
fn update_stats(pool: &Pool, service: &str, op: &str) -> Result<(), mysql::Error> {
    let mut conn = pool.get_conn()?;
    conn.exec_drop("INSERT INTO stats (service, op, visits) VALUES (?, ?, 1) ON DUPLICATE KEY UPDATE visits = visits + 1", (service, op))?;
    Ok(())
}

#[get("/concat")]
async fn concat(pool: Data<Pool>, path: web::Query<Params>) -> Result<impl Responder> {
    eprintln!("Got concat request");
    update_stats(&pool, "str", "concat").expect("Failed to update stats");
    let result = MyResult {
        res: format!("{}{}", path.a, path.b),
    };
    Ok(web::Json(result))
}

#[get("/editdistance")]
async fn editdistance(pool: Data<Pool>, path: web::Query<Params>) -> Result<impl Responder> {
    eprintln!("Got ed request");
    let ed = edit_distance(&path.a,&path.b);

    update_stats(&pool, "str", "editdistance").expect("Failed to update stats");
    let result = MyResult {
        res: format!("{}", ed),
    };
    Ok(web::Json(result))
}

#[derive(Deserialize)]
struct Param {
    a: String,
}

#[get("/upper")]
async fn upper(pool: Data<Pool>, path: web::Query<Param>) -> Result<impl Responder> {
    eprintln!("Got upper request");
    update_stats(&pool, "str", "upper").expect("Failed to update stats");
    let result = MyResult {
        res: format!("{}", path.a.to_uppercase()),
    };
    Ok(web::Json(result))
}

#[get("/lower")]
async fn lower(pool: Data<Pool>, path: web::Query<Param>) -> Result<impl Responder> {
    eprintln!("Got lower request");
    update_stats(&pool, "str", "lower").expect("Failed to update stats");
    let result = MyResult {
        res: format!("{}", path.a.to_lowercase()),
    };
    Ok(web::Json(result))
}

pub fn init(config: &mut web::ServiceConfig) {
    config.service(
        web::scope("")
            .service(concat)
            .service(upper)
            .service(lower)
            .service(editdistance)
    );
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {   
    HttpServer::new(|| {
        let url = "mysql://stats:stats@stats_db/stats_db";
        let mut pool = None;
        for _ in 0..10 {
            match Pool::new(url) {
                Ok(pool_tmp) => {
                    eprintln!("Connected to stats_db");
                    pool = Some(pool_tmp);
                    break;
                },
                Err(e) => {
                    eprintln!("Failed to connect to stats_db: {}", e);
                    std::thread::sleep(std::time::Duration::from_secs(10));
                }
            }
        }
        if pool.is_none() {
            panic!("Failed to connect to stats_db");
        }
        let pool = pool.unwrap();
        create_table(&pool).expect("Failed to create table");
        let db_data: Data<Pool> = Data::new(pool);
        App::new()
            .app_data(db_data.clone())
            .configure(init)
    })
    .bind("0.0.0.0:5000")?
    .run()
    .await
}