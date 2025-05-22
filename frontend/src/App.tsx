import React from "react"
import {Box, Color} from "@chakra-ui/react"
import EditBox from "./EditBox"
import {Button} from "./components/ui/button.tsx"
function App() {
    return <Box minH="100vh" bg='#0f0a19' px={6} py={8} >
        <div className="button_container" style={{display: "flex",}}>
            <Button style={{backgroundClip:"padding-box"}}> Editor </Button>
            <Button> Test Bench </Button>

        </div>
        <EditBox language="verilog" />
    </Box>
}
export default App;