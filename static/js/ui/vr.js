const output = document.getElementById('output');

    async function initXR() {
      if (navigator.xr) {
        const xrSession = await navigator.xr.requestSession("immersive-vr", {
          optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking']
        });

        function runAnimation() {
            window.requestAnimationFrame(runAnimation);
            for (const pad of xrSession.getGamepads()) {
              // todo; simple demo of displaying pad.axes and pad.buttons
              console.log(pad);
              Terminal.logToTerminal(`${pad}`, false);
            }
        }
        
        window.requestAnimationFrame(runAnimation);
      } else {
        alert("WebXR not supported");
      }
    }

    document.getElementById('enter-vr').addEventListener('click', initXR);