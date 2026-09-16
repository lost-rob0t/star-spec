(require :asdf)
(asdf:load-system :starlang-compiler)
(asdf:load-system :star-canonical-json)

(let* ((arguments (uiop:command-line-arguments))
       (source-path (or (first arguments)
                        (error "usage: compile_manifest.lisp SOURCE")))
       (source
         (with-open-file (stream source-path :direction :input)
           (let ((text (make-string (file-length stream))))
             (read-sequence text stream)
             text)))
       (syntax
         (starlangcompiler:read-star-syntax
          source :source-id source-path :pathname (pathname source-path)))
       (library (starlangcompiler:compile-spec-library syntax))
       (manifest (starlangcompiler:emit-portable-manifest library nil)))
  (write-string (starcanonicaljson:canonical-manifest-json manifest))
  (terpri))
