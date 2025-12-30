// webgl.js
(() => {
    const WIDTH = 1920
    const HEIGHT = 1080
    const BYTES_PER_PIXEL = 3
    const FRAME_SIZE = WIDTH * HEIGHT * BYTES_PER_PIXEL

    const canvas = document.getElementById("glcanvas")
    const gl = canvas.getContext("webgl", {
        antialias: false,
        depth: false,
        stencil: false,
        preserveDrawingBuffer: false
    })

    function resizeCanvas() {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
        gl.viewport(0, 0, canvas.width, canvas.height);
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas(); // initial call


    if (!gl) throw new Error("WebGL not supported")

    // ---------- Shaders ----------
    const VERT_SRC = `
    attribute vec2 a_pos;
    varying vec2 v_uv;
    void main() {
      v_uv = (a_pos + 1.0) * 0.5;
      gl_Position = vec4(a_pos, 0.0, 1.0);
    }
  `

    const FRAG_SRC = `
    precision mediump float;
    varying vec2 v_uv;
    uniform sampler2D u_tex;
    void main() {
      vec2 uv = vec2(v_uv.x, 1.0 - v_uv.y); // flip vertically
      gl_FragColor = texture2D(u_tex, uv);
    }
  `

    function shader(type, src) {
        const s = gl.createShader(type)
        gl.shaderSource(s, src)
        gl.compileShader(s)
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
            throw new Error(gl.getShaderInfoLog(s))
        }
        return s
    }

    const program = gl.createProgram()
    gl.attachShader(program, shader(gl.VERTEX_SHADER, VERT_SRC))
    gl.attachShader(program, shader(gl.FRAGMENT_SHADER, FRAG_SRC))
    gl.linkProgram(program)
    gl.useProgram(program)

    // ---------- Geometry ----------
    const quad = new Float32Array([
        -1, -1,
        1, -1,
        -1, 1,
        1, 1
    ])

    const vbo = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, vbo)
    gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW)

    const posLoc = gl.getAttribLocation(program, "a_pos")
    gl.enableVertexAttribArray(posLoc)
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0)

    // ---------- Texture ----------
    const tex = gl.createTexture()
    gl.bindTexture(gl.TEXTURE_2D, tex)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)

    const uTex = gl.getUniformLocation(program, "u_tex")
    gl.uniform1i(uTex, 0)

    // ---------- Frame buffer ----------
    let buffer = new Uint8Array(0)

    function appendBuffer(a, b) {
        const tmp = new Uint8Array(a.length + b.length)
        tmp.set(a)
        tmp.set(b, a.length)
        return tmp
    }

    // ---------- Render loop ----------
    window.video.on('frame', chunk => {
        buffer = appendBuffer(buffer, new Uint8Array(chunk))

        while (buffer.length >= FRAME_SIZE) {
            const frame = buffer.subarray(0, FRAME_SIZE)
            buffer = buffer.subarray(FRAME_SIZE)

            gl.activeTexture(gl.TEXTURE0)
            gl.bindTexture(gl.TEXTURE_2D, tex)

            gl.texImage2D(
                gl.TEXTURE_2D,
                0,
                gl.RGB,
                WIDTH,
                HEIGHT,
                0,
                gl.RGB,
                gl.UNSIGNED_BYTE,
                frame
            )

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
        }
    })
})()

