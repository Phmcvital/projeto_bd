-- Trigger 1: verificar sobreposição de escala
CREATE OR REPLACE FUNCTION fn_check_sobreposicao_escala()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM ESCALA
        WHERE id_residente = NEW.id_residente
          AND dia_semana   = NEW.dia_semana
          AND turno        = NEW.turno
          AND id_unidade  != NEW.id_unidade
          AND id_escala   != COALESCE(NEW.id_escala, -1)
    ) THEN
        RAISE EXCEPTION 'Residente % ja escalado no dia % turno % em outra unidade',
            NEW.id_residente, NEW.dia_semana, NEW.turno;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_sobreposicao_escala
BEFORE INSERT OR UPDATE ON ESCALA
FOR EACH ROW EXECUTE FUNCTION fn_check_sobreposicao_escala();


-- Trigger 2: auditoria de atendimento
CREATE OR REPLACE FUNCTION fn_audita_atendimento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO AUDITORIA_ATENDIMENTO (id_atendimento, operacao, usuario, dados_antigos, dados_novos)
    VALUES (
        COALESCE(NEW.id_atendimento, OLD.id_atendimento),
        TG_OP,
        current_user,
        CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE row_to_json(OLD)::JSONB END,
        CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE row_to_json(NEW)::JSONB END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_audita_atendimento
AFTER INSERT OR UPDATE OR DELETE ON ATENDIMENTO
FOR EACH ROW EXECUTE FUNCTION fn_audita_atendimento();


-- Trigger 3: atualiza média de tempo de procedimento
CREATE OR REPLACE FUNCTION fn_atualiza_media_procedimentos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE PROCEDIMENTO
    SET media_tempo_procedimento = (
        SELECT AVG(tempo_real_minutos)::NUMERIC
        FROM PROCEDIMENTO_REALIZADO
        WHERE id_procedimento = NEW.id_procedimento
    )
    WHERE id_procedimento = NEW.id_procedimento;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_atualiza_media_procedimentos
AFTER INSERT ON PROCEDIMENTO_REALIZADO
FOR EACH ROW EXECUTE FUNCTION fn_atualiza_media_procedimentos();
