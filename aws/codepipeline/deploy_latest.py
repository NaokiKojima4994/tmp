#!/usr/bin/env python3
"""
AWS CodePipeline: 最新実行のブランチ＆デプロイステータスを CSV 出力（複数パイプライン × 複数リージョン）

出力カラム:
region,pipeline,branch,deploy_stage,deploy_action,deploy_status,pipeline_status,last_update,execution_id,revision_id,revision_summary,revision_url

使い方例:
  python cp_last_deploy_csv.py \
    --pipelines my-pipeline-A my-pipeline-B \
    --regions ap-northeast-1 us-east-1 \
    --profile default \
    --deploy-stage Deploy

  # デプロイステージ名を自動検出（パイプライン定義の Deploy カテゴリのステージを探索）
  python cp_last_deploy_csv.py --pipelines my-pipeline-A --regions ap-northeast-1
"""
from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def detect_deploy_stage_name(pipeline_def: Dict, fallback: str = "Deploy") -> str:
    """
    パイプライン定義から Deploy カテゴリのステージ名を自動検出。
    見つからなければ fallback を返す。
    """
    try:
        for stage in pipeline_def["pipeline"]["stages"]:
            actions = stage.get("actions", [])
            for a in actions:
                cat = (a.get("actionTypeId", {}).get("category") or "").lower()
                if cat == "deploy":
                    return stage["name"]
    except Exception:
        pass
    return fallback


def get_source_branch_from_definition(pipeline_def: Dict) -> Optional[str]:
    """
    Source ステージの Action 設定から BranchName を取得（CodeCommit/GitHub Connections の一般的パターン）。
    取れない場合は None。
    """
    try:
        for stage in pipeline_def["pipeline"]["stages"]:
            if stage["name"].lower() == "source":
                for action in stage.get("actions", []):
                    branch = action.get("configuration", {}).get("BranchName")
                    if branch:
                        return branch
    except Exception:
        pass
    return None


def get_latest_execution_summary(cp, pipeline_name: str) -> Optional[Dict]:
    """最新実行サマリ (list-pipeline-executions の先頭) を返す。"""
    resp = cp.list_pipeline_executions(pipelineName=pipeline_name, maxResults=1)
    summaries = resp.get("pipelineExecutionSummaries", [])
    return summaries[0] if summaries else None


def get_deploy_status_for_execution(cp, pipeline_name: str, exec_id: str, deploy_stage_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    指定した実行IDに対する Deploy ステージの最新アクションのステータス/アクション名を返す。
    """
    resp = cp.list_action_executions(
        pipelineName=pipeline_name,
        filter={"pipelineExecutionId": exec_id},
    )
    details = resp.get("actionExecutionDetails", [])
    # 指定ステージに絞り、lastUpdateTime の降順で先頭を採用
    target = sorted(
        [d for d in details if d.get("stageName") == deploy_stage_name],
        key=lambda x: x.get("lastUpdateTime"),
        reverse=True,
    )
    if not target:
        return None, None
    return target[0].get("status"), target[0].get("actionName")


def get_revision_info(cp, pipeline_name: str, exec_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    実行に紐づくアーティファクトのリビジョン情報 (revisionId, revisionSummary, revisionUrl) を返す。
    """
    resp = cp.get_pipeline_execution(pipelineName=pipeline_name, pipelineExecutionId=exec_id)
    revs = (resp.get("pipelineExecution", {}) or {}).get("artifactRevisions", []) or []
    if not revs:
        return None, None, None
    r0 = revs[0]
    return r0.get("revisionId"), r0.get("revisionSummary"), r0.get("revisionUrl")


def get_pipeline_definition(cp, pipeline_name: str) -> Dict:
    return cp.get_pipeline(name=pipeline_name)


def make_cp_client(region: str, profile: Optional[str]):
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)
    return session.client("codepipeline")


def main():
    parser = argparse.ArgumentParser(description="CodePipeline: 最新実行のブランチ＆デプロイステータスを CSV で出力")
    parser.add_argument("--pipelines", nargs="+", required=True, help="対象のパイプライン名（スペース区切りで複数指定可）")
    parser.add_argument("--regions", nargs="+", required=True, help="対象のAWSリージョン（スペース区切りで複数指定可）")
    parser.add_argument("--profile", default=None, help="AWS 認証プロファイル名（省略可）")
    parser.add_argument("--deploy-stage", default=None, help="デプロイステージ名（省略時は自動検出・なければ 'Deploy'）")
    args = parser.parse_args()

    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    writer.writerow([
        "region",
        "pipeline",
        "branch",
        "deploy_stage",
        "deploy_action",
        "deploy_status",
        "pipeline_status",
        "last_update",
        "execution_id",
        "revision_id",
        "revision_summary",
        "revision_url",
    ])

    for region in args.regions:
        try:
            cp = make_cp_client(region, args.profile)
        except (BotoCoreError, ClientError) as e:
            print(f"# ERROR: failed to init client for region {region}: {e}", file=sys.stderr)
            continue

        for pipeline in args.pipelines:
            try:
                # 最新実行サマリ
                exec_summary = get_latest_execution_summary(cp, pipeline)
                if not exec_summary:
                    writer.writerow([region, pipeline, "unknown", args.deploy_stage or "Deploy", "", "", "NoExecution", "", "", "", "", ""])
                    continue

                exec_id = exec_summary.get("pipelineExecutionId")
                pipe_status = exec_summary.get("status")  # Succeeded/Failed/InProgress/Cancelled/Superseded
                last_update = exec_summary.get("lastUpdateTime")

                # パイプライン定義
                pipeline_def = get_pipeline_definition(cp, pipeline)
                branch = get_source_branch_from_definition(pipeline_def) or "unknown"

                # デプロイステージ名の決定
                deploy_stage_name = args.deploy_stage or detect_deploy_stage_name(pipeline_def, fallback="Deploy")

                # デプロイステータス（当該実行IDに対して）
                deploy_status, deploy_action = get_deploy_status_for_execution(cp, pipeline, exec_id, deploy_stage_name)

                # リビジョン情報
                rev_id, rev_summary, rev_url = get_revision_info(cp, pipeline, exec_id)

                writer.writerow([
                    region,
                    pipeline,
                    branch,
                    deploy_stage_name or "",
                    deploy_action or "",
                    deploy_status or "unknown",
                    pipe_status or "unknown",
                    last_update.isoformat() if hasattr(last_update, "isoformat") else (last_update or ""),
                    exec_id or "",
                    rev_id or "",
                    (rev_summary or "").replace('"', '""'),
                    rev_url or "",
                ])

            except (BotoCoreError, ClientError) as e:
                # 失敗時もCSVの一行を出すと後段処理が楽
                writer.writerow([region, pipeline, "error", args.deploy_stage or "Deploy", "", "", f"ERROR: {type(e).__name__}", "", "", "", str(e).replace('"', '""'), ""])
            except Exception as e:
                writer.writerow([region, pipeline, "error", args.deploy_stage or "Deploy", "", "", f"ERROR: {type(e).__name__}", "", "", "", str(e).replace('"', '""'), ""])


if __name__ == "__main__":
    main()
