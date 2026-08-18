import { useState } from "react";
import "../styles/Header.css";


function Header() {

    const [open, setOpen] = useState(false);

    return (
        <>
            <header className="header">

                <div>
                    <h1>Workspace AI</h1>
                    <p>Your Intelligent Workspace</p>
                </div>

                

                
            </header>

            

        </>
    );

}

export default Header;