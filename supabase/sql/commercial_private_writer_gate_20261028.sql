-- Source-controlled copy of Supabase migration commercial_private_writer_gate_20261028
-- Applied on 2026-10-28 to project flqxwhibxnyujynmopmr.
-- No writer identity is provisioned by this migration. Existing CRM rows are unchanged.
CREATE TABLE IF NOT EXISTS crm_sofft.commercial_writer_identities (
  identity_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE RESTRICT,
  status text NOT NULL DEFAULT 'DISABLED' CHECK (status IN ('DISABLED','ENABLED')),
  approval_ref text,
  approved_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT commercial_writer_approval_required CHECK (
    status <> 'ENABLED'
    OR (approval_ref IS NOT NULL AND length(approval_ref) >= 12
        AND approved_at IS NOT NULL)
  )
);
ALTER TABLE crm_sofft.commercial_writer_identities ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE crm_sofft.commercial_writer_identities FROM PUBLIC, anon, authenticated, service_role;

CREATE OR REPLACE FUNCTION public.imperial_commercial_draft_intake(
  p_issue_number bigint,
  p_receipt_sha256 text
) RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
DECLARE
  v_actor uuid;
  v_receipt text;
  v_ref text;
  v_lead_id uuid;
BEGIN
  v_actor := auth.uid();
  IF v_actor IS NULL
    OR COALESCE(auth.jwt()->'app_metadata'->>'imperial_commercial_writer','') <> 'enabled'
  THEN
    RAISE EXCEPTION 'COMMERCIAL_WRITER_NOT_AUTHORIZED' USING ERRCODE='42501';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM crm_sofft.commercial_writer_identities acl
    WHERE acl.identity_id = v_actor AND acl.status = 'ENABLED'
      AND acl.approval_ref IS NOT NULL AND acl.approved_at IS NOT NULL
  ) THEN
    RAISE EXCEPTION 'COMMERCIAL_WRITER_NOT_AUTHORIZED' USING ERRCODE='42501';
  END IF;

  IF p_issue_number IS NULL OR p_issue_number < 1 OR p_issue_number > 9999999999999 THEN
    RAISE EXCEPTION 'INVALID_ISSUE_NUMBER' USING ERRCODE='22023';
  END IF;
  v_receipt := encode(pg_catalog.sha256(pg_catalog.convert_to(
    '{"issue":"' || p_issue_number::text
    || '","offer":"IC-OFFER-001","repo":"oromaskevic23-cmd/IMPERIAL-Venture-Factory"}',
    'UTF8')), 'hex');
  IF p_receipt_sha256 IS NULL OR p_receipt_sha256 <> v_receipt THEN
    RAISE EXCEPTION 'INVALID_SOURCE_RECEIPT' USING ERRCODE='22023';
  END IF;

  v_ref := 'github:oromaskevic23-cmd/IMPERIAL-Venture-Factory#' || p_issue_number::text;
  INSERT INTO crm_sofft.lead_registry
    (workspace_id, demand_source, source_ref, source_receipt_hash, need, state)
  VALUES ('IMPERIAL-GLOBAL','GITHUB_ISSUES_IC_OFFER_001',v_ref,v_receipt,
          'IC-OFFER-001: automation failure audit; pending human scope/privacy review',
          'LEAD_CREATED')
  ON CONFLICT (workspace_id, demand_source, source_receipt_hash) DO NOTHING
  RETURNING lead_id INTO v_lead_id;

  RETURN pg_catalog.jsonb_build_object(
    'status',CASE WHEN v_lead_id IS NULL THEN 'DUPLICATE_IGNORED' ELSE 'DRAFT_INSERTED' END,
    'source_ref',v_ref,'dispatch_allowed',false,
    'owner_scope_approval_required',true,'payment_confirmed',false
  );
END;
$$;

REVOKE ALL ON FUNCTION public.imperial_commercial_draft_intake(bigint,text)
  FROM PUBLIC, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.imperial_commercial_draft_intake(bigint,text) TO authenticated;
COMMENT ON FUNCTION public.imperial_commercial_draft_intake(bigint,text) IS
  'Strictly draft-only commercial lead ingestion; disabled unless the architect enrolls a dedicated Supabase Auth identity in commercial_writer_identities and sets trusted app_metadata. Never approves delivery or payment.';
