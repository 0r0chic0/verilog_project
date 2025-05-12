import React, { useEffect, useState, useRef, useCallback } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import { useMonaco } from "@monaco-editor/react";
import * as monacoEditor from "monaco-editor";

import { useColorMode } from "./components/ui/color-mode.tsx";
import { CompletionFormatter } from "./components/editor/completion-formatter";

interface TextEditorProps {
  language: "verilog";
  cacheSize?: number;
}

const EditBox = ({
  language,
  cacheSize = 10,
}: TextEditorProps) => {
  const monaco = useMonaco();
  const { colorMode } = useColorMode();

  const editorRef = useRef<any>(null);
  const debounceTimerRef = useRef<number | undefined>(undefined);
  const [cachedSuggestions, setCachedSuggestions] = useState<any[]>([]);

  const suggestionsRef = useRef<any[]>([]);
  const suppressSuggestionsRef = useRef(false);

  const debouncedSuggestions = useCallback(() => {
    console.log("Suggestion mode");
    
    if (suppressSuggestionsRef.current) {
    console.log("Suggestions suppressed.");
    return;
    }
    
    //const model = monaco?.editor.getModels()[0];
    const model = editorRef.current?.getModel();

    if (!model || !model.getValue()) {
      //console.log("Shouldn't be here");
      setCachedSuggestions([]);
      return;
    }
    const position = editorRef.current.getPosition();
    const offset = model.getOffsetAt(position);
    const textBeforeCursor = model.getValue().substring(0, offset);

    if (!textBeforeCursor) {
      console.log("Shouldn't be here");
      return;
    }
    console.log("🔍 Prompt sent to backend:", textBeforeCursor);
    axios
      .post("http://localhost:8000/api/v1/generate/", {
        prompt: textBeforeCursor,
      })
      .then((response) => {
        const newCompletion = response.data.text;
        console.log("✅ API Response:", newCompletion);

        if (!newCompletion || typeof newCompletion !== "string") return;

        const newSuggestion = {
          insertText: newCompletion,
          range: {
            startLineNumber: position.lineNumber,
            startColumn: position.column,
            endLineNumber: position.lineNumber, // + (newCompletion.match(/\n/g) || []).length,
            endColumn: position.column, //+ newCompletion.length,
          },
          label: "AI Suggestion",
        };

        console.log("🧠 Caching new suggestion:", newSuggestion);
        setCachedSuggestions(prev => {
        const updated = [...prev, newSuggestion].slice(-cacheSize);
        // ← NEW: also update the ref so the provider sees the latest
        suggestionsRef.current = updated;
        return updated;
        });
      })
      .catch((error) => {
        console.error("❌ Axios request failed:", error);
      });
  }, [cacheSize]);

  const triggerSuggestionsAfterPause = useCallback(() => {
    console.log("Triggered");
    clearTimeout(debounceTimerRef.current);
    debounceTimerRef.current = window.setTimeout(() => {
      suppressSuggestionsRef.current = false;
      debouncedSuggestions();
    }, 2000); // Trigger after 1s of no typing
  }, [debouncedSuggestions]);

  useEffect(() => {
    return () => {
      window.clearTimeout(debounceTimerRef.current);
    };
  }, []);

  useEffect(() => {
    console.log("use effect")
    if (!monaco) {
      console.log("use effect error")
      return;
    }    
    const provider = monaco.languages.registerInlineCompletionsProvider(
    language,
    {
      provideInlineCompletions: (model, position) => ({
        items: suggestionsRef.current.map(s =>
          new CompletionFormatter(model, position).format(s.insertText, s.range)
        ),
      }),
      freeInlineCompletions: () => {},
    }
  );

    return () => provider.dispose();
  }, [monaco,language]);

  useEffect(() => {
    console.log("inside cache size suggestion")
    if (cachedSuggestions.length === 0){
      console.log("cache size 0") 
      return;
    }
    // next tick so React state is settled
    setTimeout(() => {
      editorRef.current?.trigger(
        "keyboard",
        "editor.action.inlineSuggest.trigger",
        {}
      );
    }, 0);
  }, [cachedSuggestions]);

  return (
    <Editor
      height="90vh"
      defaultLanguage={language}
      defaultValue="// Enter code"
      theme={colorMode === "dark" ? "vs" : "vs-dark"}
      options={{
        autoClosingBrackets: "always",
        autoClosingQuotes: "always",
        formatOnType: true,
        formatOnPaste: true,
        trimAutoWhitespace: true,
        inlineSuggest: {
          enabled: true,
        },
      }}
      onMount={(editor) => {
        editorRef.current = editor;

        // Trigger after pause on every change
        editor.onKeyUp((e) => {
          const skip = [
            monacoEditor.KeyCode.Space,
            monacoEditor.KeyCode.Backspace,
            monacoEditor.KeyCode.Tab,
          ]
          
          if (e.keyCode === monacoEditor.KeyCode.Escape) {
          suppressSuggestionsRef.current = true;
          suggestionsRef.current = [];  
          setCachedSuggestions([]);
          editor.trigger("keyboard", "hideSuggestWidget", {}); 
          return;
          }
          
          if (suppressSuggestionsRef.current) {
          return;
          }
          
          if (skip.includes(e.keyCode)) {
          return;
          
          }
          triggerSuggestionsAfterPause();
        });
      }}
    />
  );
};

export default EditBox;
